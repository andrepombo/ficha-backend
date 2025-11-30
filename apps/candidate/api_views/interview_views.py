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
from ..export_service import export_service
from ..integrations.zapi_messages import (
    send_interview_scheduled_via_zapi,
    send_interview_rescheduled_via_zapi,
    send_interview_cancelled_via_zapi,
)



class InterviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing interviews.
    
    Provides CRUD operations and additional actions for interview management.
    """
    queryset = Interview.objects.all().order_by('-scheduled_date', '-scheduled_time')
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list view.
        """
        if self.action == 'list':
            return InterviewListSerializer
        return InterviewSerializer
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user when creating an interview.
        Also logs the action and sends WhatsApp via Z-API for scheduled interviews.
        """
        interview = serializer.save(created_by=self.request.user)
        
        # Log interview creation
        ActivityLog.log_action(
            action_type='interview_scheduled',
            description=f'Entrevista "{interview.title}" agendada para o candidato "{interview.candidate.full_name}"',
            candidate=interview.candidate,
            interview=interview,
            user=self.request.user,
            request=self.request
        )
        
        # Send WhatsApp via Z-API if interview is scheduled
        if interview.status == 'scheduled':
            try:
                zapi_result = send_interview_scheduled_via_zapi(interview)
                if zapi_result.get('success'):
                    logger.info(f"Z-API message (scheduled) sent for interview {interview.id}")
                else:
                    logger.warning(f"Z-API message (scheduled) failed for interview {interview.id}: {zapi_result.get('error')}" )
            except Exception as e:
                logger.error(f"Error sending Z-API message (scheduled): {e}")
    
    def update(self, request, *args, **kwargs):
        """
        Override update to handle WhatsApp notifications for both PUT and PATCH requests.
        Also logs interview updates.
        """
        # Get the original interview before update
        interview = self.get_object()
        old_date = interview.scheduled_date
        old_time = interview.scheduled_time
        old_status = interview.status
        
        logger.info(f"Interview {interview.id} update - Old date: {old_date}, Old time: {old_time}, Status: {old_status}")
        
        # Perform the standard update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(interview, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        logger.debug("Serializer validated, performing update...")
        self.perform_update(serializer)
        
        # Get the updated interview
        updated_interview = self.get_object()
        
        logger.info(f"Interview {updated_interview.id} updated - New date: {updated_interview.scheduled_date}, New time: {updated_interview.scheduled_time}, Status: {updated_interview.status}")
        
        # Check if date or time changed
        date_changed = old_date != updated_interview.scheduled_date
        time_changed = old_time != updated_interview.scheduled_time
        status_changed = old_status != updated_interview.status
        
        logger.info(f"Changes detected - Date: {date_changed}, Time: {time_changed}, Status: {status_changed}")
        
        # Log interview updates
        if status_changed:
            action_type = f"interview_{updated_interview.status}"
            description = f'Entrevista "{updated_interview.title}" status alterado de "{old_status}" para "{updated_interview.status}"'
            
            # Map status to action types
            status_action_map = {
                'completed': 'interview_completed',
                'cancelled': 'interview_cancelled',
                'rescheduled': 'interview_rescheduled',
                'scheduled': 'interview_updated'
            }
            action_type = status_action_map.get(updated_interview.status, 'interview_updated')
            
            ActivityLog.log_action(
                action_type=action_type,
                description=description,
                candidate=updated_interview.candidate,
                interview=updated_interview,
                user=request.user if request.user.is_authenticated else None,
                old_value=old_status,
                new_value=updated_interview.status,
                request=request
            )
            # Send WhatsApp via Z-API if status changed to cancelled
            if updated_interview.status == 'cancelled':
                try:
                    zapi_result = send_interview_cancelled_via_zapi(updated_interview)
                    if zapi_result.get('success'):
                        logger.info(f"Z-API message (cancelled) sent for interview {updated_interview.id}")
                    else:
                        logger.warning(f"Z-API message (cancelled) failed for interview {updated_interview.id}: {zapi_result.get('error')}")
                except Exception as e:
                    logger.error(f"Error sending Z-API message (cancelled): {e}")
        elif date_changed or time_changed:
            ActivityLog.log_action(
                action_type='interview_rescheduled',
                description=f'Entrevista "{updated_interview.title}" reagendada (Data/Hora alterada)',
                candidate=updated_interview.candidate,
                interview=updated_interview,
                user=request.user if request.user.is_authenticated else None,
                old_value=f"{old_date} {old_time}",
                new_value=f"{updated_interview.scheduled_date} {updated_interview.scheduled_time}",
                request=request
            )
        else:
            ActivityLog.log_action(
                action_type='interview_updated',
                description=f'Entrevista "{updated_interview.title}" atualizada',
                candidate=updated_interview.candidate,
                interview=updated_interview,
                user=request.user if request.user.is_authenticated else None,
                request=request
            )
        
        # Send WhatsApp via Z-API if date or time changed and interview is still scheduled
        if (date_changed or time_changed) and updated_interview.status == 'scheduled':
            try:
                zapi_result = send_interview_rescheduled_via_zapi(updated_interview, old_date, old_time)
                if zapi_result.get('success'):
                    logger.info(f"Z-API message (rescheduled) sent for interview {updated_interview.id}")
                else:
                    logger.warning(f"Z-API message (rescheduled) failed for interview {updated_interview.id}: {zapi_result.get('error')}")
            except Exception as e:
                logger.error(f"Error sending Z-API message (rescheduled): {e}")
        else:
            logger.info(f"Skipping Z-API reschedule - No date/time change or interview not scheduled")
        
        if getattr(interview, '_prefetched_objects_cache', None):
            interview._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def perform_update(self, serializer):
        """
        Perform the actual update.
        """
        serializer.save()
    
    def list(self, request, *args, **kwargs):
        """
        List all interviews with optional filtering.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by candidate if provided
        candidate_id = request.query_params.get('candidate', None)
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Filter by interviewer if provided
        interviewer_id = request.query_params.get('interviewer', None)
        if interviewer_id:
            queryset = queryset.filter(interviewer_id=interviewer_id)
        
        # Filter by date range
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)
        
        # Filter by interview type
        interview_type = request.query_params.get('type', None)
        if interview_type and interview_type != 'all':
            queryset = queryset.filter(interview_type=interview_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming interviews (scheduled for today or future).
        """
        today = datetime.now().date()
        queryset = Interview.objects.filter(
            scheduled_date__gte=today,
            status='scheduled'
        ).order_by('scheduled_date', 'scheduled_time')
        
        serializer = InterviewListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """
        Get interviews for calendar view with date range.
        """
        # Get month and year from query params, default to current month
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)
        
        if month and year:
            try:
                month = int(month)
                year = int(year)
                # Get first and last day of the month
                from calendar import monthrange
                _, last_day = monthrange(year, month)
                start_date = datetime(year, month, 1).date()
                end_date = datetime(year, month, last_day).date()
                
                queryset = Interview.objects.filter(
                    scheduled_date__gte=start_date,
                    scheduled_date__lte=end_date
                ).order_by('scheduled_date', 'scheduled_time')
            except (ValueError, TypeError):
                queryset = Interview.objects.all().order_by('scheduled_date', 'scheduled_time')
        else:
            # Default to current month
            today = datetime.now()
            from calendar import monthrange
            _, last_day = monthrange(today.year, today.month)
            start_date = datetime(today.year, today.month, 1).date()
            end_date = datetime(today.year, today.month, last_day).date()
            
            queryset = Interview.objects.filter(
                scheduled_date__gte=start_date,
                scheduled_date__lte=end_date
            ).order_by('scheduled_date', 'scheduled_time')
        
        serializer = InterviewListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update only the status of an interview.
        """
        interview = self.get_object()
        old_status = interview.status
        new_status = request.data.get('status')
        
        if new_status not in dict(Interview.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        interview.status = new_status
        interview.save()

        # Send WhatsApp via Z-API if status changed to cancelled
        if new_status == 'cancelled':
            try:
                zapi_result = send_interview_cancelled_via_zapi(interview)
                if zapi_result.get('success'):
                    logger.info(f"Z-API message (cancelled) sent for interview {interview.id}")
                else:
                    logger.warning(f"Z-API message (cancelled) failed for interview {interview.id}: {zapi_result.get('error')}")
            except Exception as e:
                logger.error(f"Error sending Z-API message (cancelled): {e}")
        
        serializer = self.get_serializer(interview)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def add_feedback(self, request, pk=None):
        """
        Add feedback and rating to an interview.
        """
        interview = self.get_object()
        
        feedback = request.data.get('feedback', '')
        rating = request.data.get('rating', None)
        
        interview.feedback = feedback
        if rating:
            interview.rating = rating
        
        # Automatically mark as completed if feedback is added
        if feedback and interview.status == 'scheduled':
            interview.status = 'completed'
        
        interview.save()
        
        serializer = self.get_serializer(interview)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about interviews.
        """
        total = Interview.objects.count()
        status_counts = Interview.objects.values('status').annotate(count=Count('status'))
        
        # Get upcoming interviews count
        today = datetime.now().date()
        upcoming_count = Interview.objects.filter(
            scheduled_date__gte=today,
            status='scheduled'
        ).count()
        
        # Get today's interviews
        today_count = Interview.objects.filter(
            scheduled_date=today,
            status='scheduled'
        ).count()
        
        stats = {
            'total': total,
            'upcoming': upcoming_count,
            'today': today_count,
            'by_status': {item['status']: item['count'] for item in status_counts},
        }
        
        return Response(stats)


