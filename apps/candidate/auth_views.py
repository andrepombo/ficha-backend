from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import os
from django.core.cache import cache
from .models import DemoVisitor


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get the current authenticated user's information
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_superuser': user.is_superuser,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def demo_login(request):
    """
    One-click demo login: issues JWT tokens for a demo user and redirects to the dashboard,
    after storing tokens in localStorage. Optional query param `redirect` controls the target path.
    """
    username = os.environ.get('DEMO_USER_USERNAME', 'demo')
    password = os.environ.get('DEMO_USER_PASSWORD', 'demo123!')

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': os.environ.get('DEMO_USER_EMAIL', 'demo@example.com'),
            'is_staff': False,
            'is_superuser': False,
        },
    )
    if created:
        user.set_password(password)
        user.save()

    # Basic IP rate limiting (30 hits/hour per IP)
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', 'unknown')
    except Exception:
        ip = 'unknown'
    key = f"demo_login:{ip}"
    cnt = cache.get(key)
    if cnt is None:
        cache.set(key, 1, timeout=3600)
    else:
        if cnt >= 30:
            return HttpResponse('<h1>Too Many Requests</h1><p>Please try again later.</p>', status=429)
        try:
            cache.incr(key)
        except Exception:
            cache.set(key, cnt + 1, timeout=3600)

    # Issue JWT token pair
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    refresh_token = str(refresh)

    # Where to send the user after storing tokens
    redirect_to = request.GET.get('redirect', '/painel/dashboard')

    # Small HTML/JS page that stores tokens and redirects
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <meta name=\"robots\" content=\"noindex, nofollow\" />
    <title>Signing you in…</title>
    <style>
      body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; display:flex; align-items:center; justify-content:center; min-height:100vh; background:#f8fafc; color:#0f172a; }}
      .card {{ background:#fff; padding:24px 28px; border-radius:12px; box-shadow: 0 10px 25px rgba(2,6,23,0.08); max-width: 420px; text-align:center; }}
      .spinner {{ width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px; }}
      @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>
  </head>
  <body>
    <div class=\"card\">
      <div class=\"spinner\"></div>
      <h1>Entrando no modo demo…</h1>
      <p>Você será redirecionado em instantes.</p>
    </div>
    <script>
      try {{
        localStorage.setItem('access_token', {access!r});
        localStorage.setItem('refresh_token', {refresh_token!r});
        // Clear any cached user so app refetches
        localStorage.removeItem('user');
      }} catch (e) {{
        console.error('Failed to store tokens', e);
      }}
      window.location.replace({redirect_to!r});
    </script>
  </body>
  </html>"""

    return HttpResponse(html, content_type='text/html')


class DemoAwareTokenObtainPairView(TokenObtainPairView):
    """Override token obtain to support demo password and capture visitor email."""

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        visitor_email = request.data.get('visitor_email') or username or ''

        demo_username = os.environ.get('DEMO_USER_USERNAME', 'demo')
        demo_password = os.environ.get('DEMO_USER_PASSWORD', '12345')
        demo_email = os.environ.get('DEMO_USER_EMAIL', 'demo@example.com')

        if password == demo_password:
            user, created = User.objects.get_or_create(
                username=demo_username,
                defaults={
                    'email': demo_email,
                    'is_staff': False,
                    'is_superuser': False,
                },
            )

            # Ensure password is set to the demo password
            if created or not user.check_password(demo_password):
                user.set_password(demo_password)
                user.save()

            # Store the visitor's provided email for tracking
            # Track visitor email without losing the demo account identity
            if visitor_email:
                demo_record, _ = DemoVisitor.objects.get_or_create(email=visitor_email)
                demo_record.visit_count = demo_record.visit_count + 1
                demo_record.save(update_fields=['visit_count', 'last_seen'])

            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    'access': access,
                    'refresh': refresh_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_superuser': user.is_superuser,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return super().post(request, *args, **kwargs)
