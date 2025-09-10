import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from agent.llm import generate_response, stream_response_text
from kb.retrieve import retrieve_with_fallback


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        payload = json.loads(text_data)
        message = payload.get('message', '').strip()
        if not message:
            return

        context, docs = await sync_to_async(retrieve_with_fallback)(message)
        sources = []
        for d in docs:
            label = d.title
            link = d.uri or ''
            origin = 'External Source' if d.source == 'external' else label
            sources.append((origin, link))

        text = await sync_to_async(generate_response)(context, message)
        for chunk in stream_response_text(text):
            await self.send(json.dumps({'type': 'chunk', 'content': chunk}))

        citations = []
        for title, link in sources:
            if link:
                citations.append(f"(Source: {title}, {link})")
            else:
                citations.append(f"(Source: {title})")

        disclaimer = 'This information is for educational purposes only. Please consult a licensed financial advisor for decisions.\nEducational use only.'
        await self.send(json.dumps({'type': 'done', 'citations': citations, 'disclaimer': disclaimer}))

