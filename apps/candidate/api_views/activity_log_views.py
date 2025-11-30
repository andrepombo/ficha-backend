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



class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing activity logs.
    
    Provides read and delete operations for activity log tracking.
    Only superusers can delete logs.
    """
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Only superusers can delete activity logs.
        """
        if self.action in ['destroy', 'bulk_delete']:
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list view.
        """
        if self.action == 'list':
            return ActivityLogListSerializer
        return ActivityLogSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all activity logs with optional filtering.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by action type if provided
        action_type_filter = request.query_params.get('action_type', None)
        if action_type_filter and action_type_filter != 'all':
            queryset = queryset.filter(action_type=action_type_filter)
        
        # Filter by candidate if provided
        candidate_id = request.query_params.get('candidate', None)
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        # Filter by user if provided
        user_id = request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by date range
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Limit to recent logs if limit parameter is provided
        limit = request.query_params.get('limit', None)
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent activity logs (last 50 by default).
        """
        limit = request.query_params.get('limit', 50)
        try:
            limit = int(limit)
        except ValueError:
            limit = 50
        
        queryset = self.get_queryset()[:limit]
        serializer = ActivityLogListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get activity log statistics.
        """
        try:
            queryset = self.get_queryset()
            
            # Filter by date range if provided
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            # Get action type counts
            from django.db.models import Count
            action_type_counts = []
            for action_type, display in ActivityLog.ACTION_TYPES:
                count = queryset.filter(action_type=action_type).count()
                if count > 0:
                    action_type_counts.append({
                        'action_type': action_type,
                        'action_type_display': display,
                        'count': count
                    })
            
            # Get user activity counts
            user_activity = []
            user_counts = queryset.values('user__username', 'user__first_name', 'user__last_name').annotate(count=Count('id')).order_by('-count')[:10]
            for item in user_counts:
                if item['user__username']:
                    user_activity.append(item)
            
            # Get daily activity for the last 30 days
            from django.utils import timezone
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            daily_logs = queryset.filter(timestamp__gte=thirty_days_ago)
            
            # Group by date
            daily_activity = {}
            for log in daily_logs:
                date_str = log.timestamp.date().isoformat()
                if date_str in daily_activity:
                    daily_activity[date_str] += 1
                else:
                    daily_activity[date_str] = 1
            
            daily_activity_list = [{'day': day, 'count': count} for day, count in sorted(daily_activity.items())]
            
            return Response({
                'total_activities': queryset.count(),
                'action_type_counts': action_type_counts,
                'top_users': user_activity,
                'daily_activity': daily_activity_list,
            })
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc(),
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Bulk delete activity logs by IDs.
        Only superusers can perform this action.
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Apenas superusuários podem deletar logs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'Nenhum ID fornecido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = ActivityLog.objects.filter(id__in=ids).delete()
        
        return Response({
            'deleted_count': deleted_count,
            'message': f'{deleted_count} log(s) deletado(s) com sucesso.'
        })


