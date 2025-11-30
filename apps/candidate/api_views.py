from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Candidate, Interview
from .serializers import (
    CandidateSerializer,
    CandidateListSerializer,
    CandidateStatusUpdateSerializer,
    CandidateNotesUpdateSerializer,
    InterviewSerializer,
    InterviewListSerializer,
    UserSerializer
)
from django.contrib.auth.models import User
from .whatsapp_service import whatsapp_service
from .export_service import export_service
import logging

logger = logging.getLogger(__name__)


class CandidateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing candidates.
    
    Provides CRUD operations and additional actions for candidate management.
    """
    queryset = Candidate.objects.all().order_by('-applied_date')
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    
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
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update only the status of a candidate.
        """
        candidate = self.get_object()
        serializer = CandidateStatusUpdateSerializer(candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_notes(self, request, pk=None):
        """
        Update only the notes of a candidate.
        """
        candidate = self.get_object()
        serializer = CandidateNotesUpdateSerializer(candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def interviews(self, request, pk=None):
        """
        Get all interviews for a specific candidate.
        """
        candidate = self.get_object()
        interviews = Interview.objects.filter(candidate=candidate).order_by('-scheduled_date', '-scheduled_time')
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
            from .scoring_config import ScoringConfig
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
            from .scoring_config import ScoringConfig
            
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
            from .scoring_config import ScoringConfig
            success, message = ScoringConfig.reset_to_defaults()
            
            if success:
                default_weights = ScoringConfig.DEFAULT_WEIGHTS
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
        Also sends WhatsApp notification to the candidate.
        """
        interview = serializer.save(created_by=self.request.user)
        
        print(f"[WhatsApp] Interview {interview.id} created with status: {interview.status}")
        
        # Send WhatsApp notification if interview is scheduled
        if interview.status == 'scheduled':
            print(f"[WhatsApp] Attempting to send scheduled message for interview {interview.id}")
            try:
                result = whatsapp_service.send_interview_scheduled_message(interview)
                
                if result['success']:
                    # Update interview with WhatsApp tracking info
                    interview.whatsapp_sent = True
                    interview.whatsapp_message_sid = result.get('message_sid', '')
                    interview.whatsapp_sent_at = timezone.now()
                    interview.save(update_fields=['whatsapp_sent', 'whatsapp_message_sid', 'whatsapp_sent_at'])
                    
                    logger.info(f"WhatsApp notification sent for interview {interview.id}")
                else:
                    logger.warning(f"Failed to send WhatsApp for interview {interview.id}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error sending WhatsApp notification: {e}")
    
    def update(self, request, *args, **kwargs):
        """
        Override update to handle WhatsApp notifications for both PUT and PATCH requests.
        """
        # Get the original interview before update
        interview = self.get_object()
        old_date = interview.scheduled_date
        old_time = interview.scheduled_time
        old_status = interview.status
        
        print(f"[WhatsApp] Interview {interview.id} update - Old date: {old_date}, Old time: {old_time}, Status: {old_status}")
        logger.info(f"[WhatsApp] Interview {interview.id} update - Old date: {old_date}, Old time: {old_time}, Status: {old_status}")
        
        # Perform the standard update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(interview, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(f"[WhatsApp] Serializer validated, performing update...")
        self.perform_update(serializer)
        
        # Get the updated interview
        updated_interview = self.get_object()
        
        print(f"[WhatsApp] Interview {updated_interview.id} updated - New date: {updated_interview.scheduled_date}, New time: {updated_interview.scheduled_time}, Status: {updated_interview.status}")
        logger.info(f"[WhatsApp] Interview {updated_interview.id} updated - New date: {updated_interview.scheduled_date}, New time: {updated_interview.scheduled_time}, Status: {updated_interview.status}")
        
        # Check if date or time changed
        date_changed = old_date != updated_interview.scheduled_date
        time_changed = old_time != updated_interview.scheduled_time
        status_changed = old_status != updated_interview.status
        
        print(f"[WhatsApp] Changes detected - Date: {date_changed}, Time: {time_changed}, Status: {status_changed}")
        logger.info(f"[WhatsApp] Changes detected - Date: {date_changed}, Time: {time_changed}, Status: {status_changed}")
        
        # Send WhatsApp notification if date or time changed and interview is still scheduled
        if (date_changed or time_changed) and updated_interview.status == 'scheduled':
            print(f"[WhatsApp] Sending rescheduling notification for interview {updated_interview.id}")
            logger.info(f"[WhatsApp] Sending rescheduling notification for interview {updated_interview.id}")
            try:
                result = whatsapp_service.send_interview_rescheduled_message(
                    updated_interview,
                    old_date=old_date,
                    old_time=old_time
                )
                
                if result['success']:
                    print(f"[WhatsApp] ✅ Rescheduling notification sent for interview {updated_interview.id}")
                    print(f"[WhatsApp] Message SID: {result.get('message_sid')}, Phone used: {result.get('verified_phone')}")
                    logger.info(f"[WhatsApp] ✅ Rescheduling notification sent for interview {updated_interview.id}")
                else:
                    print(f"[WhatsApp] ❌ Failed to send rescheduling: {result.get('error')}")
                    logger.warning(f"[WhatsApp] ❌ Failed to send rescheduling: {result.get('error')}")
            except Exception as e:
                print(f"[WhatsApp] ❌ Error sending rescheduling notification: {e}")
                logger.error(f"[WhatsApp] ❌ Error sending rescheduling notification: {e}")
        else:
            logger.info(f"[WhatsApp] Skipping notification - No date/time change or interview not scheduled")
        
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
        Sends WhatsApp notifications when status changes to cancelled or rescheduled.
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
        
        # Send WhatsApp notification based on status change
        try:
            if new_status == 'cancelled' and old_status != 'cancelled':
                result = whatsapp_service.send_interview_cancelled_message(interview)
                if result['success']:
                    logger.info(f"WhatsApp cancellation sent for interview {interview.id}")
                else:
                    logger.warning(f"Failed to send WhatsApp cancellation: {result.get('error')}")
            
            elif new_status == 'rescheduled' and old_status != 'rescheduled':
                result = whatsapp_service.send_interview_rescheduled_message(interview)
                if result['success']:
                    logger.info(f"WhatsApp rescheduling notification sent for interview {interview.id}")
                else:
                    logger.warning(f"Failed to send WhatsApp rescheduling: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error sending WhatsApp status notification: {e}")
        
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


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing users (for interviewer selection).
    """
    queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
