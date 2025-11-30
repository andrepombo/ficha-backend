from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('apply/', views.application_form_view, name='application_form'),
    path('success/', views.application_success_view, name='application_success'),
    path('login/', views.candidate_login_view, name='candidate_login'),
    path('status/', views.candidate_status_view, name='candidate_status'),
    path('password/reset/', views.candidate_password_reset_request, name='candidate_password_reset_request'),
    path('password/verify/', views.candidate_password_reset_verify, name='candidate_password_reset_verify'),
    path('logout/', views.candidate_logout_view, name='candidate_logout'),
    path('test-partial/', TemplateView.as_view(template_name='candidate/test_partial_save.html'), name='test_partial_save'),
]
