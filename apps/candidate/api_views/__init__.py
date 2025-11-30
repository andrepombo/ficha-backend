"""
API views package for the candidate app.

This package organizes API viewsets into separate modules for better maintainability:
- candidate_views.py: CandidateViewSet for managing candidates
- interview_views.py: InterviewViewSet for managing interviews
- activity_log_views.py: ActivityLogViewSet for viewing activity logs
- user_views.py: UserViewSet for listing users
"""

from .candidate_views import CandidateViewSet
from .interview_views import InterviewViewSet
from .activity_log_views import ActivityLogViewSet
from .user_views import UserViewSet

__all__ = [
    'CandidateViewSet',
    'InterviewViewSet',
    'ActivityLogViewSet',
    'UserViewSet',
]
