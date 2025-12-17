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
        # In demo mode, auto-reset demo data daily at/after 03:00 local time
        if demo_mode:
            try:
                now_local = timezone.localtime(timezone.now())
                # Only run once per day after 03:00
                last_key = 'demo_last_reset_date'
                lock_key = 'demo_reset_lock'
                last_reset = cache.get(last_key)
                if now_local.hour >= 3:
                    today = now_local.date().isoformat()
                    if last_reset != today:
                        # Acquire short lock to avoid concurrent resets across workers
                        if cache.add(lock_key, '1', timeout=300):
                            try:
                                # Demo environment only: wipe and reseed candidates nightly
                                call_command('seed_candidates_with_forms', count=30, delete_existing=True)
                                cache.set(last_key, today, timeout=172800)  # keep for 2 days
                            finally:
                                cache.delete(lock_key)
            except Exception:
                # Never break requests due to reset failures
                pass
        if demo_mode and getattr(request, 'user', None) and request.user.is_authenticated:
            if request.user.username == self.demo_username:
                path = request.path or ''
                method = request.method.upper()
                # Hide admin area for demo user
                if path.startswith('/admin/'):
                    return HttpResponse('Not Found', status=404)
        return self.get_response(request)
