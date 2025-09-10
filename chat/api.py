from django.urls import path, re_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from agent.llm import generate_response
from agent.tools import amortization_schedule, apr_to_apy, debt_to_income_ratio
from kb.retrieve import retrieve_with_fallback
from .models import ChatSession, Message


@api_view(['POST'])
def chat_api(request):
    data = request.data
    text = data.get('message', '').strip()
    session_id = data.get('session_id')
    if not text:
        return Response({'error': 'message required'}, status=400)

    with transaction.atomic():
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create()
        else:
            session = ChatSession.objects.create()
        Message.objects.create(session=session, role='user', content=text)

    # Tool detection (simple heuristics)
    tool_result = None
    if 'amortization' in text.lower():
        # very basic parse e.g., "amortization 100000 0.05 30"
        parts = [p for p in text.split() if p.replace('.', '', 1).isdigit()]
        if len(parts) >= 3:
            principal = float(parts[0])
            rate = float(parts[1])
            years = int(float(parts[2]))
            tool_result = amortization_schedule(principal, rate, years)
    elif 'apr' in text.lower() and 'apy' in text.lower():
        # e.g., "apr 0.199 apy"
        parts = [p for p in text.split() if p.replace('.', '', 1).isdigit()]
        if parts:
            apr = float(parts[0])
            tool_result = {
                'apy': round(apr_to_apy(apr), 6)
            }
    elif 'dti' in text.lower() or 'debt-to-income' in text.lower():
        # e.g., "dti 1500 6000"
        parts = [p for p in text.split() if p.replace('.', '', 1).isdigit()]
        if len(parts) >= 2:
            debt = float(parts[0])
            income = float(parts[1])
            tool_result = {
                'dti': round(debt_to_income_ratio(debt, income), 4)
            }

    context, docs = retrieve_with_fallback(text)
    sources = []
    for d in docs:
        label = d.title
        link = d.uri or ''
        sources.append({'title': label, 'link': link, 'source': d.source})

    llm_text = generate_response(context, text)

    if tool_result is not None:
        tool_section = "\n\nCalculated result (using tools):\n" + str(tool_result)
    else:
        tool_section = ''

    citations = []
    for s in sources:
        if s.get('link'):
            citations.append(f"(Source: {s['title']}, {s['link']})")
        else:
            origin = 'External Source' if s.get('source') == 'external' else s['title']
            citations.append(f"(Source: {origin})")

    disclaimer = '\n\nThis information is for educational purposes only. Please consult a licensed financial advisor for decisions.\nEducational use only.'
    answer = llm_text + tool_section + "\n\n" + " ".join(citations) + disclaimer

    with transaction.atomic():
        msg = Message.objects.create(session=session, role='assistant', content=answer, sources=sources)

    return Response({'session_id': session.id, 'message_id': msg.id, 'answer': answer, 'sources': sources})


@api_view(['POST'])
def sync_kb(request):
    from kb.tasks import task_ingest_path
    path = request.data.get('path', '')
    if not path:
        return Response({'error': 'path required'}, status=400)
    task = task_ingest_path.delay(path)
    return Response({'task_id': task.id})


urlpatterns = [
    path('chat/', chat_api, name='chat_api'),
    path('sync/', sync_kb, name='sync_kb'),
]

# ---- Tools APIs ----

@api_view(['POST'])
def calc_amortization(request):
    data = request.data
    try:
        principal = float(data.get('principal', 0))
        apr_percent = float(data.get('apr_percent', 0))
        years = int(float(data.get('years', 0)))
    except Exception:
        return Response({'error': 'invalid parameters'}, status=400)
    if principal <= 0 or years <= 0 or apr_percent < 0:
        return Response({'error': 'principal > 0, years > 0, apr_percent >= 0 required'}, status=400)

    # Convert APR percent to decimal annual rate expected by amortization_schedule
    result = amortization_schedule(principal, apr_percent / 100.0, years)

    # Optionally log into a session
    session_id = data.get('session_id')
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create()
        Message.objects.create(
            session=session,
            role='assistant',
            content=f"Amortization: principal={principal}, apr%={apr_percent}, years={years}. Monthly={result['monthly_payment']}, Total Interest={result['total_interest']}",
            sources=[{'tool': 'amortization', 'inputs': {'principal': principal, 'apr_percent': apr_percent, 'years': years}, 'result': result}],
        )

    return Response(result)


@api_view(['POST'])
def calc_apy(request):
    data = request.data
    try:
        apr_percent = float(data.get('apr_percent', 0))
        periods = int(data.get('periods', 12))
    except Exception:
        return Response({'error': 'invalid parameters'}, status=400)
    if apr_percent < 0 or periods <= 0:
        return Response({'error': 'apr_percent >= 0 and periods > 0 required'}, status=400)
    apy = apr_to_apy(apr_percent / 100.0, periods)

    session_id = data.get('session_id')
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create()
        Message.objects.create(
            session=session,
            role='assistant',
            content=f"APR→APY: apr%={apr_percent}, n={periods}. APY={(round(apy*100, 6))}%",
            sources=[{'tool': 'apr_to_apy', 'inputs': {'apr_percent': apr_percent, 'periods': periods}, 'result': {'apy': apy}}],
        )

    return Response({'apy': apy})


@api_view(['POST'])
def calc_dti(request):
    data = request.data
    try:
        debt = float(data.get('debt', 0))
        income = float(data.get('income', 0))
    except Exception:
        return Response({'error': 'invalid parameters'}, status=400)
    if income <= 0 or debt < 0:
        return Response({'error': 'income > 0 and debt >= 0 required'}, status=400)
    dti = debt_to_income_ratio(debt, income)
    result = {'dti': dti}

    session_id = data.get('session_id')
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create()
        Message.objects.create(
            session=session,
            role='assistant',
            content=f"DTI: debt={debt}, income={income}. DTI={(round(dti*100, 4))}%",
            sources=[{'tool': 'dti', 'inputs': {'debt': debt, 'income': income}, 'result': result}],
        )

    return Response(result)


# ---- Sessions APIs ----

@api_view(['GET', 'POST'])
def sessions_api(request):
    if request.method == 'POST':
        title = (request.data.get('title') or '').strip()
        s = ChatSession.objects.create(title=title)
        return Response({'id': s.id, 'title': s.title, 'created_at': s.created_at})

    # GET list
    out = []
    for s in ChatSession.objects.order_by('-created_at')[:50]:
        out.append({'id': s.id, 'title': s.title, 'created_at': s.created_at, 'message_count': s.messages.count()})
    return Response(out)


@api_view(['GET', 'PATCH'])
def session_detail_api(request, id: int):
    try:
        s = ChatSession.objects.get(id=id)
    except ChatSession.DoesNotExist:
        return Response({'error': 'not found'}, status=404)
    if request.method == 'PATCH':
        title = (request.data.get('title') or '').strip()
        s.title = title
        s.save(update_fields=['title'])
        return Response({'id': s.id, 'title': s.title})
    # GET
    msgs = [
        {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'sources': m.sources,
            'created_at': m.created_at,
        }
        for m in s.messages.order_by('-created_at')[:200]
    ]
    return Response({'id': s.id, 'title': s.title, 'messages': msgs})


urlpatterns += [
    path('tools/amortization/', calc_amortization, name='calc_amortization'),
    path('tools/apy/', calc_apy, name='calc_apy'),
    path('tools/dti/', calc_dti, name='calc_dti'),
    path('sessions/', sessions_api, name='sessions'),
    re_path(r'^sessions/(?P<id>\d+)/$', session_detail_api, name='session_detail'),
]
