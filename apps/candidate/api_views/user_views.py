"""
API views for the candidate app.
This module has been split from a single file for better maintainability.
"""
from .base import (
    viewsets, status, action, Response, IsAuthenticated,
    Count, Q, HttpResponse, datetime, timedelta, timezone, logger
)
from ..models import Candidate, Interview, ActivityLog
from ..serializers import (
    CandidateSerializer,
    CandidateListSerializer,
    CandidateStatusUpdateSerializer,
    CandidateNotesUpdateSerializer,
    InterviewSerializer,
    InterviewListSerializer,
    UserSerializer,
    ActivityLogSerializer,
    ActivityLogListSerializer
)
from django.contrib.auth.models import User
from ..whatsapp_service import whatsapp_service
from ..export_service import export_service



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing users (for interviewer selection).
    """
    queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for users list

