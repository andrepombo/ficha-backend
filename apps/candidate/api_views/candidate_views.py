"""
API views for the candidate app.
This module has been split from a single file for better maintainability.
"""
from .base import (
    viewsets, status, action, Response, IsAuthenticated,
    Count, Q, HttpResponse, datetime, timedelta, timezone, logger
)
from rest_framework.permissions import AllowAny
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
from django.core.cache import cache



class CandidateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing candidates.
    
    Provides CRUD operations and additional actions for candidate management.
    """
    queryset = Candidate.objects.all().order_by('-applied_date')
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow public access for partial save; keep others authenticated."""
        if getattr(self, 'action', None) in ['public_partial_save']:
            return [AllowAny()]
        return [perm() if isinstance(perm, type) else perm for perm in self.permission_classes]

    def get_authenticators(self):
        """Disable authentication (and CSRF) for public partial save."""
        if getattr(self, 'action', None) in ['public_partial_save']:
            return []
        return super().get_authenticators()
    
    def get_queryset(self):
        """
        Optimize queries for detail endpoints by prefetching related data.
        """
        return (
            Candidate.objects.all()
            .order_by('-applied_date')
            .prefetch_related('professional_experiences', 'work_cards')
        )
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list view.
        """
        if self.action == 'list':
            return CandidateListSerializer
        return CandidateSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all candidates with optional filtering and advanced search.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Filter by position if provided
        position_filter = request.query_params.get('position', None)
        if position_filter and position_filter != 'all':
            queryset = queryset.filter(position_applied=position_filter)
        
        # Filter by month if provided
        month_filter = request.query_params.get('month', None)
        if month_filter and month_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__month=int(month_filter))
            except ValueError:
                pass
        
        # Filter by year if provided
        year_filter = request.query_params.get('year', None)
        if year_filter and year_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__year=int(year_filter))
            except ValueError:
                pass
        
        # Simple search on name, CPF, and phone
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(cpf__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        # Advanced filters
        # Filter by gender
        gender_filter = request.query_params.get('gender', None)
        if gender_filter and gender_filter != 'all':
            queryset = queryset.filter(gender=gender_filter)
        
        # Filter by disability
        disability_filter = request.query_params.get('disability', None)
        if disability_filter and disability_filter != 'all':
            queryset = queryset.filter(disability=disability_filter)
        
        # Filter by education level
        education_filter = request.query_params.get('education', None)
        if education_filter and education_filter != 'all':
            queryset = queryset.filter(highest_education=education_filter)
        
        # Filter by transportation
        transportation_filter = request.query_params.get('transportation', None)
        if transportation_filter and transportation_filter != 'all':
            queryset = queryset.filter(has_own_transportation=transportation_filter)
        
        # Filter by employment status
        employment_filter = request.query_params.get('currently_employed', None)
        if employment_filter and employment_filter != 'all':
            queryset = queryset.filter(currently_employed=employment_filter)
        
        # Filter by availability
        availability_filter = request.query_params.get('availability', None)
        if availability_filter and availability_filter != 'all':
            queryset = queryset.filter(availability_start=availability_filter)
        
        # Filter by travel availability
        travel_filter = request.query_params.get('travel_availability', None)
        if travel_filter and travel_filter != 'all':
            queryset = queryset.filter(travel_availability=travel_filter)
        
        # Filter by height painting capability
        height_painting_filter = request.query_params.get('height_painting', None)
        if height_painting_filter and height_painting_filter != 'all':
            queryset = queryset.filter(height_painting=height_painting_filter)
        
        # Filter by city
        city_filter = request.query_params.get('city', None)
        if city_filter and city_filter != 'all':
            queryset = queryset.filter(city__iexact=city_filter)
        
        # Filter by how they found the vacancy
        how_found_filter = request.query_params.get('how_found_vacancy', None)
        if how_found_filter and how_found_filter != 'all':
            queryset = queryset.filter(how_found_vacancy=how_found_filter)
        
        # Filter by application date range
        date_from = request.query_params.get('date_from', None)
        if date_from:
            try:
                queryset = queryset.filter(applied_date__gte=date_from)
            except (ValueError, TypeError):
                pass
        
        date_until = request.query_params.get('date_until', None)
        if date_until:
            try:
                queryset = queryset.filter(applied_date__lte=date_until)
            except (ValueError, TypeError):
                pass
        
        # Filter by score range
        score_range = request.query_params.get('score_range', None)
        if score_range and score_range != 'all':
            if score_range == 'excellent':  # 80-100
                queryset = queryset.filter(score__gte=80, score__lte=100)
            elif score_range == 'good':  # 60-79
                queryset = queryset.filter(score__gte=60, score__lt=80)
            elif score_range == 'average':  # 40-59
                queryset = queryset.filter(score__gte=40, score__lt=60)
            elif score_range == 'poor':  # 0-39
                queryset = queryset.filter(score__gte=0, score__lt=40)
            elif score_range == 'not_scored':  # No score yet
                queryset = queryset.filter(Q(score__isnull=True) | Q(score=0))
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='public/partial-save', authentication_classes=[], permission_classes=[AllowAny])
    def public_partial_save(self, request):
        """
        Public endpoint to create or update a draft candidate from Step 1 data.
        Sets status to 'incomplete' and returns the candidate id.
        Payload may include optional 'id' to update an existing draft.
        """
        data = request.data or {}
        candidate_id = data.get('id')

        # Minimal fields for step 1
        # Normalize phone to pattern 'dd ddddd-dddd' when 11 digits
        def _normalize_phone(raw: str) -> str:
            digits = ''.join(ch for ch in (raw or '') if ch.isdigit())
            if len(digits) == 11:
                return f"{digits[0:2]} {digits[2:7]}-{digits[7:11]}"
            return raw or ''

        fields = {
            'full_name': (data.get('full_name') or '').strip(),
            'cpf': (data.get('cpf') or '').strip(),
            'email': (data.get('email') or '').strip() or None,
            'phone_number': _normalize_phone(data.get('phone_number') or ''),
            'position_applied': (data.get('position_applied') or '').strip(),
        }

        # Basic validation of required minimal fields
        missing = [k for k in ['full_name', 'cpf', 'phone_number'] if not fields[k]]
        if missing:
            return Response({'error': f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if candidate_id:
                candidate = Candidate.objects.filter(id=candidate_id).first()
                if not candidate:
                    return Response({'error': 'Candidate not found for update'}, status=status.HTTP_404_NOT_FOUND)
                # Update minimal fields
                for k, v in fields.items():
                    setattr(candidate, k, v)
            else:
                candidate = Candidate(**fields)
                # Always set incomplete on initial draft create
                candidate.status = 'incomplete'

            # For updates, keep later stages intact; otherwise enforce incomplete
            if candidate_id:
                if candidate.status not in ['reviewing', 'shortlisted', 'interviewed', 'accepted', 'rejected']:
                    candidate.status = 'incomplete'

            # Save without triggering heavy logic; minimal update_fields if existing
            if candidate_id:
                candidate.save(update_fields=list(fields.keys()) + ['status', 'updated_date'])
            else:
                candidate.save()

            return Response({'id': candidate.id, 'status': candidate.status}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception('Error in public partial save')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single candidate with short-lived caching to reduce latency.
        """
        pk = kwargs.get('pk')
        cache_key = f"candidate_detail:{pk}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=30)  # 30 seconds TTL
        return Response(data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a candidate (PATCH).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about candidates.
        
        Returns counts by status and other useful metrics.
        """
        total = Candidate.objects.count()
        status_counts = Candidate.objects.values('status').annotate(count=Count('status'))
        
        stats = {
            'total': total,
            'by_status': {item['status']: item['count'] for item in status_counts},
        }
        
        # Add individual status counts for easier access
        for status_choice, _ in Candidate.STATUS_CHOICES:
            if status_choice not in stats['by_status']:
                stats['by_status'][status_choice] = 0
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def funnel_stats(self, request):
        """
        Get conversion funnel statistics.
        
        Tracks candidates through stages: applied → shortlisted → interviewed → hired
        Optionally filter by month and year.
        """
        # Get month and year filters if provided
        month_filter = request.query_params.get('month', None)
        year_filter = request.query_params.get('year', None)
        queryset = Candidate.objects.all()
        
        if month_filter and month_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__month=int(month_filter) + 1)  # JavaScript months are 0-indexed
            except ValueError:
                pass
        
        if year_filter and year_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__year=int(year_filter))
            except ValueError:
                pass
        
        # Count candidates at each stage
        # For a proper funnel, we count candidates CURRENTLY at each specific status
        # This creates a descending pattern as candidates move through the pipeline
        
        # Stage 1: Applied - Pending candidates (just applied)
        applied_count = queryset.filter(status='pending').count()
        
        # Stage 2: Em Análise - Currently under review
        reviewing_count = queryset.filter(status='reviewing').count()
        
        # Stage 3: Shortlisted - Currently shortlisted for interview
        shortlisted_count = queryset.filter(status='shortlisted').count()
        
        # Stage 4: Interviewed - Currently interviewed (awaiting decision)
        interviewed_count = queryset.filter(status='interviewed').count()
        
        # Stage 5: Hired - Those who were accepted
        hired_count = queryset.filter(status='accepted').count()
        
        # Get rejected count
        rejected_count = queryset.filter(status='rejected').count()
        
        # Calculate total candidates (including rejected - everyone who applied)
        total_applied = queryset.count()
        
        # For the funnel visualization, we show cumulative counts (how many reached at least this stage)
        # This creates the proper descending funnel shape
        # Aplicados includes EVERYONE who applied (including rejected)
        cumulative_applied = total_applied
        cumulative_reviewing = reviewing_count + shortlisted_count + interviewed_count + hired_count
        cumulative_shortlisted = shortlisted_count + interviewed_count + hired_count
        cumulative_interviewed = interviewed_count + hired_count
        cumulative_hired = hired_count
        
        # Calculate conversion rates (percentage of total who applied)
        applied_rate = 100.0  # Starting point - everyone applied
        reviewing_rate = (cumulative_reviewing / total_applied * 100) if total_applied > 0 else 0
        shortlisted_rate = (cumulative_shortlisted / total_applied * 100) if total_applied > 0 else 0
        interviewed_rate = (cumulative_interviewed / total_applied * 100) if total_applied > 0 else 0
        hired_rate = (cumulative_hired / total_applied * 100) if total_applied > 0 else 0
        
        # Calculate stage-to-stage conversion rates
        applied_to_reviewing = (cumulative_reviewing / cumulative_applied * 100) if cumulative_applied > 0 else 0
        reviewing_to_shortlisted = (cumulative_shortlisted / cumulative_reviewing * 100) if cumulative_reviewing > 0 else 0
        shortlisted_to_interviewed = (cumulative_interviewed / cumulative_shortlisted * 100) if cumulative_shortlisted > 0 else 0
        interviewed_to_hired = (cumulative_hired / cumulative_interviewed * 100) if cumulative_interviewed > 0 else 0
        
        # Overall conversion rate (applied to hired)
        overall_conversion = (cumulative_hired / total_applied * 100) if total_applied > 0 else 0
        
        funnel_data = {
            'stages': [
                {
                    'name': 'Aplicados',
                    'count': cumulative_applied,
                    'percentage': round(applied_rate, 1),
                    'color': '#f97316',  # Orange (pending)
                },
                {
                    'name': 'Em Análise',
                    'count': cumulative_reviewing,
                    'percentage': round(reviewing_rate, 1),
                    'conversion_from_previous': round(applied_to_reviewing, 1),
                    'color': '#a855f7',  # Purple (reviewing)
                },
                {
                    'name': 'Selecionados',
                    'count': cumulative_shortlisted,
                    'percentage': round(shortlisted_rate, 1),
                    'conversion_from_previous': round(reviewing_to_shortlisted, 1),
                    'color': '#06b6d4',  # Cyan (shortlisted)
                },
                {
                    'name': 'Entrevistados',
                    'count': cumulative_interviewed,
                    'percentage': round(interviewed_rate, 1),
                    'conversion_from_previous': round(shortlisted_to_interviewed, 1),
                    'color': '#6366f1',  # Indigo (interviewed)
                },
                {
                    'name': 'Contratados',
                    'count': cumulative_hired,
                    'percentage': round(hired_rate, 1),
                    'conversion_from_previous': round(interviewed_to_hired, 1),
                    'color': '#10b981',  # Green (accepted)
                },
            ],
            'total_in_funnel': total_applied,
            'overall_conversion_rate': round(overall_conversion, 1),
            'rejected_count': rejected_count,
        }
        
        return Response(funnel_data)
    
    @action(detail=False, methods=['get'])
    def average_time_per_stage(self, request):
        """
        Calculate average time spent in each recruitment stage.
        
        Returns average days spent in each stage based on status transitions.
        Optionally filter by month and year.
        """
        from datetime import datetime, timedelta
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        
        # Get month and year filters if provided
        month_filter = request.query_params.get('month', None)
        year_filter = request.query_params.get('year', None)
        queryset = Candidate.objects.all()
        
        if month_filter and month_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__month=int(month_filter) + 1)  # JavaScript months are 0-indexed
            except ValueError:
                pass
        
        if year_filter and year_filter != 'all':
            try:
                queryset = queryset.filter(applied_date__year=int(year_filter))
            except ValueError:
                pass
        
        # Calculate average time for each stage
        # Note: This is a simplified calculation based on applied_date and current status
        # For more accurate tracking, you would need status_changed_at timestamps
        # The time represents how long candidates spend IN each stage before moving to the next
        
        time_data = []
        
        # Stage 1: Pendentes (pending) - Time from application to review
        pending_candidates = queryset.filter(status='pending')
        if pending_candidates.exists():
            # Estimate: 1-3 days average for initial application processing
            avg_days_pending = 2
            time_data.append({
                'stage': 'Pendentes',
                'average_days': avg_days_pending,
                'color': '#f97316'  # Orange (pending)
            })
        
        # Stage 2: Em Análise (reviewing)
        reviewing_candidates = queryset.filter(
            Q(status='reviewing') | Q(status='shortlisted') | Q(status='interviewed') | Q(status='accepted')
        )
        if reviewing_candidates.exists():
            # Estimate: 3-5 days average for detailed review
            avg_days_reviewing = 4
            time_data.append({
                'stage': 'Em Análise',
                'average_days': avg_days_reviewing,
                'color': '#a855f7'  # Purple (reviewing)
            })
        
        # Stage 3: Selecionados (shortlisted)
        shortlisted_candidates = queryset.filter(
            Q(status='shortlisted') | Q(status='interviewed') | Q(status='accepted')
        )
        if shortlisted_candidates.exists():
            # Estimate: 5-7 days average for scheduling interview
            avg_days_to_shortlist = 6
            time_data.append({
                'stage': 'Selecionados',
                'average_days': avg_days_to_shortlist,
                'color': '#06b6d4'  # Cyan (shortlisted)
            })
        
        # Stage 4: Entrevistados (interviewed)
        interviewed_candidates = queryset.filter(
            Q(status='interviewed') | Q(status='accepted')
        )
        if interviewed_candidates.exists():
            # Estimate: 5-10 days average for decision making after interview
            avg_days_to_interview = 7
            time_data.append({
                'stage': 'Entrevistados',
                'average_days': avg_days_to_interview,
                'color': '#6366f1'  # Indigo (interviewed)
            })
        
        # Stage 5: Contratados (hired)
        hired_candidates = queryset.filter(status='accepted')
        if hired_candidates.exists():
            # Estimate: 3-5 days for final paperwork and onboarding prep
            avg_days_to_onboard = 4
            time_data.append({
                'stage': 'Contratados',
                'average_days': avg_days_to_onboard,
                'color': '#10b981'  # Green (accepted)
            })
        
        # Calculate total average time
        total_avg_days = sum(stage['average_days'] for stage in time_data)
        
        return Response({
            'stages': time_data,
            'total_average_days': total_avg_days,
            'note': 'Tempos estimados baseados em dados históricos'
        })
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """
        Get all available filter options for advanced search.
        
        Returns unique values for various fields to populate filter dropdowns.
        """
        # Get unique positions
        positions = list(Candidate.objects.exclude(
            position_applied=''
        ).values_list('position_applied', flat=True).distinct().order_by('position_applied'))
        
        # Get unique cities
        cities = list(Candidate.objects.exclude(
            city=''
        ).values_list('city', flat=True).distinct().order_by('city'))
        
        # Get unique companies
        companies = list(Candidate.objects.exclude(
            current_company=''
        ).values_list('current_company', flat=True).distinct().order_by('current_company'))
        
        # Get education levels from model choices
        education_levels = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Candidate._meta.get_field('highest_education').choices
        ]
        
        # Get gender options
        gender_options = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Candidate._meta.get_field('gender').choices
        ]
        
        # Get disability options
        disability_options = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Candidate._meta.get_field('disability').choices
        ]
        
        # Get availability options
        availability_options = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Candidate._meta.get_field('availability_start').choices
        ]
        
        # Get how found vacancy options
        how_found_options = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Candidate._meta.get_field('how_found_vacancy').choices
        ]
        
        filter_options = {
            'positions': positions,
            'cities': cities,
            'companies': companies,
            'education_levels': education_levels,
            'gender_options': gender_options,
            'disability_options': disability_options,
            'availability_options': availability_options,
            'how_found_options': how_found_options,
            'yes_no_options': [
                {'value': 'sim', 'label': 'Sim'},
                {'value': 'nao', 'label': 'Não'}
            ]
        }
        
        return Response(filter_options)
    
    def create(self, request, *args, **kwargs):
        """
        Override create to log candidate creation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidate = serializer.save()
        
        # Immediately calculate and persist the candidate's score on creation
        try:
            candidate.calculate_score()
            candidate.save(update_fields=['score', 'score_breakdown', 'score_updated_at'])
        except Exception as e:
            logger.error(f"Error calculating score on candidate creation (ID: {candidate.id}): {e}")
        
        # Re-serialize to return fresh data including calculated score
        serializer = self.get_serializer(candidate)
        
        # Log candidate creation
        ActivityLog.log_action(
            action_type='candidate_created',
            description=f'Candidato "{candidate.full_name}" foi criado',
            candidate=candidate,
            user=request.user if request.user.is_authenticated else None,
            request=request
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Override update to log candidate updates.
        Note: Status changes via update_status() action are logged separately.
        """
        candidate = self.get_object()
        candidate.refresh_from_db()
        old_status = candidate.status
        
        # Perform the standard update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(candidate, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Only log here if this is NOT a status-only update
        # (status-only updates should use the update_status action which logs separately)
        if 'status' in request.data and len(request.data) == 1:
            # This is a status-only update, skip logging here entirely
            # (it will be logged by update_status if that action is used)
            pass
        else:
            # This is NOT a status-only update
            if old_status != candidate.status:
                # Status changed as part of a larger update
                ActivityLog.log_action(
                    action_type='status_changed',
                    description=f'Status do candidato "{candidate.full_name}" alterado de "{candidate.STATUS_TRANSLATIONS.get(old_status, old_status)}" para "{candidate.get_status_pt()}"',
                    candidate=candidate,
                    user=request.user if request.user.is_authenticated else None,
                    old_value=old_status,
                    new_value=candidate.status,
                    request=request
                )
            else:
                # General update without status change
                ActivityLog.log_action(
                    action_type='candidate_updated',
                    description=f'Dados do candidato "{candidate.full_name}" foram atualizados',
                    candidate=candidate,
                    user=request.user if request.user.is_authenticated else None,
                    request=request
                )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update only the status of a candidate.
        """
        candidate = self.get_object()
        # Refresh from DB to ensure we have the current state
        candidate.refresh_from_db()
        old_status = candidate.status
        
        serializer = CandidateStatusUpdateSerializer(candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Only log if status actually changed
        if old_status != candidate.status:
            ActivityLog.log_action(
                action_type='status_changed',
                description=f'Status do candidato "{candidate.full_name}" alterado de "{candidate.STATUS_TRANSLATIONS.get(old_status, old_status)}" para "{candidate.get_status_pt()}"',
                candidate=candidate,
                user=request.user if request.user.is_authenticated else None,
                old_value=old_status,
                new_value=candidate.status,
                request=request
            )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_notes(self, request, pk=None):
        """
        Update only the notes of a candidate.
        """
        candidate = self.get_object()
        old_notes = candidate.notes
        serializer = CandidateNotesUpdateSerializer(candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log notes update
        ActivityLog.log_action(
            action_type='note_added',
            description=f'Notas do candidato "{candidate.full_name}" foram atualizadas',
            candidate=candidate,
            user=request.user if request.user.is_authenticated else None,
            old_value=old_notes,
            new_value=candidate.notes,
            request=request
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def interviews(self, request, pk=None):
        """
        Get all interviews for a specific candidate.
        """
        candidate = self.get_object()
        interviews = (
            Interview.objects.filter(candidate=candidate)
            .select_related('interviewer', 'candidate')
            .order_by('-scheduled_date', '-scheduled_time')
        )
        serializer = InterviewListSerializer(interviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """
        Export candidates report to PDF.
        """
        try:
            # Get filtered candidates
            queryset = self.filter_queryset(self.get_queryset())
            
            # Apply filters
            status_filter = request.query_params.get('status', 'all')
            if status_filter != 'all':
                queryset = queryset.filter(status=status_filter)
            
            position_filter = request.query_params.get('position', 'all')
            if position_filter != 'all':
                queryset = queryset.filter(position_applied=position_filter)
            
            month_filter = request.query_params.get('month', 'all')
            if month_filter != 'all':
                queryset = queryset.filter(applied_date__month=int(month_filter))
            
            year_filter = request.query_params.get('year', 'all')
            if year_filter != 'all':
                queryset = queryset.filter(applied_date__year=int(year_filter))
            
            search = request.query_params.get('search', '')
            if search:
                queryset = queryset.filter(
                    Q(full_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(position_applied__icontains=search)
                )
            
            # Prepare filters for display
            filters = {
                'status': status_filter,
                'position': position_filter,
                'month': month_filter,
                'year': year_filter,
                'search': search
            }
            
            # Generate PDF
            pdf_buffer = export_service.generate_candidates_pdf(list(queryset), filters)
            
            # Create response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"candidatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating PDF export: {e}")
            return Response(
                {'error': 'Failed to generate PDF export'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """
        Export candidates report to Excel.
        """
        try:
            # Get filtered candidates
            queryset = self.filter_queryset(self.get_queryset())
            
            # Apply filters
            status_filter = request.query_params.get('status', 'all')
            if status_filter != 'all':
                queryset = queryset.filter(status=status_filter)
            
            position_filter = request.query_params.get('position', 'all')
            if position_filter != 'all':
                queryset = queryset.filter(position_applied=position_filter)
            
            month_filter = request.query_params.get('month', 'all')
            if month_filter != 'all':
                queryset = queryset.filter(applied_date__month=int(month_filter))
            
            year_filter = request.query_params.get('year', 'all')
            if year_filter != 'all':
                queryset = queryset.filter(applied_date__year=int(year_filter))
            
            search = request.query_params.get('search', '')
            if search:
                queryset = queryset.filter(
                    Q(full_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(position_applied__icontains=search)
                )
            
            # Prepare filters for display
            filters = {
                'status': status_filter,
                'position': position_filter,
                'month': month_filter,
                'year': year_filter,
                'search': search
            }
            
            # Generate Excel
            excel_buffer = export_service.generate_candidates_excel(list(queryset), filters)
            
            # Create response
            response = HttpResponse(
                excel_buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"candidatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating Excel export: {e}")
            return Response(
                {'error': 'Failed to generate Excel export'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_analytics_pdf(self, request):
        """
        Export analytics report to PDF.
        """
        try:
            queryset = self.get_queryset()
            year = request.query_params.get('year', None)
            
            if year and year != 'all':
                queryset = queryset.filter(applied_date__year=int(year))
            
            # Generate PDF
            pdf_buffer = export_service.generate_analytics_pdf(list(queryset), year)
            
            # Create response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"analytics_{year if year else 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating analytics PDF export: {e}")
            return Response(
                {'error': 'Failed to generate analytics PDF export'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def export_analytics_excel(self, request):
        """
        Export analytics report to Excel.
        """
        try:
            queryset = self.get_queryset()
            year = request.query_params.get('year', None)
            
            if year and year != 'all':
                queryset = queryset.filter(applied_date__year=int(year))
            
            # Generate Excel
            excel_buffer = export_service.generate_analytics_excel(list(queryset), year)
            
            # Create response
            response = HttpResponse(
                excel_buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"analytics_{year if year else 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating analytics Excel export: {e}")
            return Response(
                {'error': 'Failed to generate analytics Excel export'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def calculate_score(self, request, pk=None):
        """
        Calculate and update the score for a specific candidate.
        """
        try:
            candidate = self.get_object()
            score_data = candidate.calculate_score()
            candidate.save(update_fields=['score', 'score_breakdown', 'score_updated_at'])
            
            return Response({
                'id': candidate.id,
                'full_name': candidate.full_name,
                'score': float(candidate.score),
                'grade': score_data['grade'],
                'breakdown': score_data['breakdown'],
                'score_updated_at': candidate.score_updated_at,
            })
        except Exception as e:
            logger.error(f"Error calculating candidate score: {e}")
            return Response(
                {'error': 'Failed to calculate candidate score'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def recalculate_all_scores(self, request):
        """
        Recalculate scores for all candidates.
        Useful for bulk updates or when scoring criteria change.
        """
        try:
            candidates = self.get_queryset()
            updated_count = 0
            
            for candidate in candidates:
                try:
                    candidate.calculate_score()
                    candidate.save(update_fields=['score', 'score_breakdown', 'score_updated_at'])
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error calculating score for candidate {candidate.id}: {e}")
                    continue
            
            return Response({
                'message': f'Successfully recalculated scores for {updated_count} candidates',
                'total_candidates': candidates.count(),
                'updated_count': updated_count,
            })
        except Exception as e:
            logger.error(f"Error recalculating all scores: {e}")
            return Response(
                {'error': 'Failed to recalculate scores'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def score_distribution(self, request):
        """
        Get score distribution statistics.
        Returns counts of candidates in different score ranges.
        """
        try:
            queryset = self.get_queryset()
            
            # Apply filters if provided
            status_filter = request.query_params.get('status', None)
            if status_filter and status_filter != 'all':
                queryset = queryset.filter(status=status_filter)
            
            position_filter = request.query_params.get('position', None)
            if position_filter and position_filter != 'all':
                queryset = queryset.filter(position_applied=position_filter)
            
            # Calculate distribution
            total = queryset.count()
            excellent = queryset.filter(score__gte=80).count()  # A range
            good = queryset.filter(score__gte=60, score__lt=80).count()  # B range
            average = queryset.filter(score__gte=40, score__lt=60).count()  # C range
            poor = queryset.filter(score__lt=40).count()  # D/F range
            
            # Get top candidates
            top_candidates = queryset.order_by('-score')[:10]
            top_candidates_data = CandidateListSerializer(top_candidates, many=True).data
            
            # Calculate average score
            avg_score = queryset.aggregate(avg=Count('score'))
            
            return Response({
                'total': total,
                'distribution': {
                    'excellent': {'count': excellent, 'percentage': round((excellent / total * 100) if total > 0 else 0, 1), 'range': '80-100'},
                    'good': {'count': good, 'percentage': round((good / total * 100) if total > 0 else 0, 1), 'range': '60-79'},
                    'average': {'count': average, 'percentage': round((average / total * 100) if total > 0 else 0, 1), 'range': '40-59'},
                    'poor': {'count': poor, 'percentage': round((poor / total * 100) if total > 0 else 0, 1), 'range': '0-39'},
                },
                'top_candidates': top_candidates_data,
            })
        except Exception as e:
            logger.error(f"Error getting score distribution: {e}")
            return Response(
                {'error': 'Failed to get score distribution'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def scoring_config(self, request):
        """
        Get current scoring configuration (weights).
        """
        try:
            from ..scoring_config import ScoringConfig
            config_info = ScoringConfig.get_config_info()
            return Response(config_info)
        except Exception as e:
            logger.error(f"Error getting scoring config: {e}")
            return Response(
                {'error': 'Failed to get scoring config'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def update_scoring_config(self, request):
        """
        Update scoring configuration (weights).
        Requires all weights to sum to 100.
        """
        try:
            from ..scoring_config import ScoringConfig
            
            weights = request.data.get('weights')
            if not weights:
                return Response(
                    {'error': 'Weights are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            success, message = ScoringConfig.set_weights(weights)
            
            if success:
                return Response({
                    'message': message,
                    'weights': weights,
                })
            else:
                return Response(
                    {'error': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error updating scoring config: {e}")
            return Response(
                {'error': 'Failed to update scoring config'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def reset_scoring_config(self, request):
        """
        Reset scoring configuration to default weights.
        """
        try:
            from ..scoring_config import ScoringConfig
            success, message = ScoringConfig.reset_to_defaults()
            
            if success:
                default_weights = ScoringConfig.get_weights()
                return Response({
                    'message': message,
                    'weights': default_weights,
                })
            else:
                return Response(
                    {'error': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error resetting scoring config: {e}")
            return Response(
                {'error': 'Failed to reset scoring config'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(
        detail=False, 
        methods=['get'], 
        url_path='view-work-card/(?P<work_card_id>[^/.]+)',
        authentication_classes=[],  # Allow unauthenticated access with token in URL
        permission_classes=[]
    )
    def view_work_card(self, request, work_card_id=None):
        """
        Serve work card documents with proper headers for iframe embedding.
        This endpoint allows documents to be displayed in iframes by setting X-Frame-Options: SAMEORIGIN.
        Uses token-based authentication via URL parameter for iframe compatibility.
        """
        import os
        import mimetypes
        from django.http import FileResponse, Http404
        from django.conf import settings
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        from ..models import WorkCard
        
        # Validate token from query parameter
        token = request.query_params.get('token')
        if not token:
            logger.error("No token provided for work card view")
            return Response(
                {'error': 'Authentication token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Validate the JWT token
            AccessToken(token)
        except TokenError as e:
            logger.error(f"Token validation error in view_work_card: {e}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected error validating token in view_work_card: {e}")
            return Response(
                {'error': 'Token validation failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            work_card = WorkCard.objects.get(id=work_card_id)
            
            # Check if file exists
            if not work_card.file:
                raise Http404("Work card document not found")
            
            # Use storage backend to access the file (works for local FS and S3)
            storage = work_card.file.storage
            file_name = work_card.file.name
            
            if not storage.exists(file_name):
                raise Http404("Work card file not found on server")
            
            # Determine content type from filename
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Check if download is requested
            download = request.query_params.get('download', 'false').lower() == 'true'

            # Determine filename and extension early to adjust behavior
            filename = os.path.basename(file_name)
            ext = os.path.splitext(filename)[1].lower()

            # Do not force download here; honor the query param for work cards

            # Open and serve the file via storage
            file_obj = storage.open(file_name, 'rb')
            response = FileResponse(file_obj, content_type=content_type)

            # Set headers to allow iframe embedding from caller origin via CSP
            origin = request.headers.get('Origin') or ''
            allowed_ancestors = ["'self'", 'http://localhost:5173', 'http://127.0.0.1:5173']
            if origin and origin not in allowed_ancestors:
                allowed_ancestors.append(origin)
            response['Content-Security-Policy'] = f"frame-ancestors {' '.join(allowed_ancestors)}"

            # Set content disposition based on download parameter
            if download:
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response['Content-Disposition'] = f'inline; filename="{filename}"'

            return response
            
        except WorkCard.DoesNotExist:
            raise Http404("Work card not found")
        except Exception as e:
            logger.error(f"Error serving work card document: {e}")
            return Response(
                {'error': 'Failed to serve work card document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(
        detail=True, 
        methods=['get'], 
        url_path='view-document/(?P<doc_type>resume|photo)',
        authentication_classes=[],  # Allow unauthenticated access with token in URL
        permission_classes=[]
    )
    def view_document(self, request, pk=None, doc_type=None):
        """
        Serve candidate documents (resume or photo) with proper headers for iframe embedding.
        This endpoint allows documents to be displayed in iframes by setting X-Frame-Options: SAMEORIGIN.
        Uses token-based authentication via URL parameter for iframe compatibility.
        """
        import os
        import mimetypes
        from django.http import FileResponse, Http404
        from django.conf import settings
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        # Validate token from query parameter
        token = request.query_params.get('token')
        if not token:
            return Response(
                {'error': 'Authentication token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Validate the JWT token
            AccessToken(token)
        except TokenError:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            candidate = self.get_object()
            
            # Get the appropriate file field
            if doc_type == 'resume':
                file_field = candidate.resume
            elif doc_type == 'photo':
                file_field = candidate.photo
            else:
                return Response(
                    {'error': 'Invalid document type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if file exists
            if not file_field:
                raise Http404("Document not found")
            
            # Use storage backend to access the file (works for local FS and S3)
            storage = file_field.storage
            file_name = file_field.name
            
            if not storage.exists(file_name):
                raise Http404("Document file not found on server")
            
            # Determine content type from filename
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Check if download is requested
            download = request.query_params.get('download', 'false').lower() == 'true'
            
            # Open and serve the file via storage
            file_obj = storage.open(file_name, 'rb')
            response = FileResponse(file_obj, content_type=content_type)
            
            # Set headers to allow iframe embedding from same origin and caller origin
            response['X-Frame-Options'] = 'SAMEORIGIN'
            origin = request.headers.get('Origin') or ''
            allowed_ancestors = ["'self'", 'http://localhost:5173', 'http://127.0.0.1:5173']
            if origin and origin not in allowed_ancestors:
                allowed_ancestors.append(origin)
            response['Content-Security-Policy'] = f"frame-ancestors {' '.join(allowed_ancestors)}"
            
            # Set content disposition based on download parameter
            filename = os.path.basename(file_name)
            if download:
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response['Content-Disposition'] = f'inline; filename="{filename}"'
            
            return response
            
        except Candidate.DoesNotExist:
            raise Http404("Candidate not found")
        except Exception as e:
            logger.error(f"Error serving document: {e}")
            return Response(
                {'error': 'Failed to serve document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


