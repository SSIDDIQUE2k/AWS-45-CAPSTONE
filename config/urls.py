from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.http import require_GET

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chat.api')),
    path('favicon.ico', favicon_view),
    
    # Main pages
    path('', TemplateView.as_view(template_name='landing/index.html'), name='home'),
    path('chat/', TemplateView.as_view(template_name='chat/index.html'), name='chat'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard'),
    
    # Authentication
    path('auth/login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('auth/register/', TemplateView.as_view(template_name='auth/register.html'), name='register'),
    path('auth/forgot-password/', TemplateView.as_view(template_name='auth/forgot-password.html'), name='forgot_password'),
    
    # Tools and Features
    path('calculators/', TemplateView.as_view(template_name='tools/calculators.html'), name='calculators'),
    path('budget/', TemplateView.as_view(template_name='tools/budget.html'), name='budget'),
    path('goals/', TemplateView.as_view(template_name='tools/goals.html'), name='goals'),
    path('investments/', TemplateView.as_view(template_name='tools/investments.html'), name='investments'),
    
    # Learning
    path('courses/', TemplateView.as_view(template_name='learn/courses.html'), name='courses'),
    path('library/', TemplateView.as_view(template_name='learn/library.html'), name='library'),
    path('community/', TemplateView.as_view(template_name='learn/community.html'), name='community'),
    
    # Legacy routes (for backward compatibility)
    path('landing/', TemplateView.as_view(template_name='financial_ai_landing/index.html'), name='financial_ai_landing'),
    path('tools/', TemplateView.as_view(template_name='financial_ai_landing/ai_tools.html'), name='ai_tools'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
