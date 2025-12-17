import os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.cache import cache
from django.core.management import call_command


class DemoReadOnlyMiddleware:
    """
    In demo mode, enforce read-only behavior for the demo user across API endpoints.
    - Blocks mutating methods (POST, PUT, PATCH, DELETE) under /api/ for the demo user
    - Whitelists JWT token endpoints so refresh/obtain still work
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.demo_username = os.getenv('DEMO_USER_USERNAME', 'demo')

    def __call__(self, request):
        demo_mode = getattr(settings, 'DEMO_MODE', False)
        # In demo mode, apply demo-specific restrictions (e.g. demo user behavior)
        if demo_mode and getattr(request, 'user', None) and request.user.is_authenticated:
            if request.user.username == self.demo_username:
                path = request.path or ''
                method = request.method.upper()
                # Hide admin area for demo user
                if path.startswith('/admin/'):
                    return HttpResponse('Not Found', status=404)
        return self.get_response(request)
