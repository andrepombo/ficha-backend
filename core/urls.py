"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.candidate.auth_views import current_user
from apps.candidate import views
from apps.candidate.webhook_views import whatsapp_webhook

urlpatterns = [
    # Multi-step application form
    path('', views.position_selection_view, name='position_selection'),  # Step 0: Position selection (NEW DEFAULT)
    path('form/', views.application_form_view, name='application_form'),  # Step 1: Dados Pessoais
    path('success/', views.application_success_view, name='application_success'),
    path('login/', views.candidate_login_view, name='candidate_login'),
    path('status/', views.candidate_status_view, name='candidate_status'),
    path('edit/', views.candidate_edit_view, name='candidate_edit'),
    path('password/reset/', views.candidate_password_reset_request, name='candidate_password_reset_request'),
    path('password/verify/', views.candidate_password_reset_verify, name='candidate_password_reset_verify'),
    path('logout/', views.candidate_logout_view, name='candidate_logout'),
    path('test-partial/', TemplateView.as_view(template_name='candidate/test_partial_save.html'), name='test_partial_save'),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # WhatsApp webhook
    path('webhooks/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
    
    # Privacy Policy
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    
    # API endpoints
    path('api/', include('apps.candidate.api_urls')),
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', current_user, name='current_user'),
]

# Serve media and static files
# Note: In production, you should use a proper web server (Nginx/Apache) to serve these files
# For now, we'll serve them through Django for simplicity
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
