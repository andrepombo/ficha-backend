from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.db.models import Count, Avg, Q, F
from django.db import transaction
from django.conf import settings
from decimal import Decimal
import json
import os

from ..models import (
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    CandidateQuestionnaireResponse,
    CandidateSelectedOption,
    Candidate,
)
from ..serializers import (
    QuestionnaireTemplateSerializer,
    QuestionnaireTemplatePublicSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    CandidateQuestionnaireResponseSerializer,
    SubmitQuestionnaireSerializer,
)


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing questionnaire templates.
    Only admins can create/update/delete templates.
    """
    queryset = QuestionnaireTemplate.objects.all().prefetch_related('questions__options')
    serializer_class = QuestionnaireTemplateSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        """Allow public access for submit so candidates can save steps; keep others admin-only."""
        if self.action in ['submit']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        """Use public serializer for non-admin users."""
        if self.action in ['active_for_position', 'public_detail']:
            return QuestionnaireTemplatePublicSerializer
        return QuestionnaireTemplateSerializer
    
    def get_permissions(self):
        """Allow public access for specific actions."""
        if self.action in ['active_for_position', 'public_detail', 'steps_for_position']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'], url_path='active')
    def active_for_position(self, request):
        """
        Get the first active questionnaire template for a specific position.
        DEPRECATED: Use steps-for-position endpoint for multiple questionnaires.
        Query param: position_key
        """
        position_key = request.query_params.get('position_key')
        if not position_key:
            return Response(
                {'error': 'position_key query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the first active questionnaire ordered by step_number
        template = QuestionnaireTemplate.objects.prefetch_related(
            'questions__options'
        ).filter(
            position_key=position_key,
            is_active=True
        ).order_by('step_number').first()
        
        if not template:
            return Response(
                {'error': f'No active questionnaire found for position: {position_key}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='steps-for-position')
    def steps_for_position(self, request):
        """
        Get all active questionnaire steps for a specific position, ordered by step_number.
        Query param: position_key
        Returns: List of questionnaire templates ordered by step
        """
        position_key = request.query_params.get('position_key')
        if not position_key:
            return Response(
                {'error': 'position_key query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = QuestionnaireTemplate.objects.prefetch_related(
            'questions__options'
        ).filter(
            position_key=position_key,
            is_active=True
        ).order_by('step_number')
        
        serializer = self.get_serializer(templates, many=True)
        return Response({
            'position_key': position_key,
            'total_steps': templates.count(),
            'steps': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate this template (multiple templates can be active per position)."""
        template = self.get_object()
        template.is_active = True
        template.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate this template."""
        template = self.get_object()
        template.is_active = False
        template.save()
        return Response({'status': 'deactivated'})
    
    @action(detail=True, methods=['post'])
    def update_step(self, request, pk=None):
        """Update the step_number for this template."""
        template = self.get_object()
        step_number = request.data.get('step_number')
        
        if step_number is None:
            return Response(
                {'error': 'step_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            step_number = int(step_number)
            if step_number < 1:
                raise ValueError('step_number must be >= 1')
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid step_number: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template.step_number = step_number
        template.save()
        return Response({'status': 'updated', 'step_number': step_number})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for this questionnaire template."""
        template = self.get_object()
        responses = CandidateQuestionnaireResponse.objects.filter(template=template)
        
        stats = {
            'total_responses': responses.count(),
            'average_score': responses.aggregate(Avg('score'))['score__avg'] or 0,
            'average_percentage': responses.aggregate(
                avg_pct=Avg(
                    (100.0 * models.F('score')) / models.F('max_score')
                )
            )['avg_pct'] or 0,
        }
        
        return Response(stats)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing questions within templates.
    Only admins can create/update/delete questions.
    """
    queryset = Question.objects.all().prefetch_related('options')
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter by template if provided."""
        queryset = super().get_queryset()
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset
    
    def perform_create(self, serializer):
        """Ensure template_id is provided."""
        template_id = self.request.data.get('template_id')
        if not template_id:
            raise ValueError('template_id is required')
        serializer.save(template_id=template_id)


class QuestionOptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing question options.
    Only admins can create/update/delete options.
    """
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter by question if provided."""
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset
    
    def perform_create(self, serializer):
        """Ensure question_id is provided."""
        question_id = self.request.data.get('question_id')
        if not question_id:
            raise ValueError('question_id is required')
        
        # Get option_points from request
        option_points = self.request.data.get('option_points', 0)
        print(f"DEBUG PERFORM_CREATE: Received option_points={option_points}")
        
        # Pass option_points directly to save - this should work now
        instance = serializer.save(question_id=question_id, option_points=option_points)
        
        # Verify it was saved
        instance.refresh_from_db()
        print(f"DEBUG PERFORM_CREATE: After save and refresh, option_points={instance.option_points}")
        
        if instance.option_points != option_points:
            print(f"WARNING: option_points mismatch! Expected {option_points}, got {instance.option_points}")
            # Force it with raw SQL if needed
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE candidate_questionoption SET option_points = %s WHERE id = %s",
                    [option_points, instance.id]
                )
            instance.refresh_from_db()
            print(f"DEBUG PERFORM_CREATE: After SQL update, option_points={instance.option_points}")


class CandidateQuestionnaireResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing candidate questionnaire responses.
    Admins can view all responses.
    """
    queryset = CandidateQuestionnaireResponse.objects.all().select_related(
        'candidate', 'template'
    ).prefetch_related('selected_options__option')
    serializer_class = CandidateQuestionnaireResponseSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter by candidate or position if provided."""
        queryset = super().get_queryset()
        candidate_id = self.request.query_params.get('candidate_id')
        position_key = self.request.query_params.get('position_key')
        
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        if position_key:
            queryset = queryset.filter(position_key=position_key)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='submit')
    def submit(self, request):
        """
        Submit a questionnaire response for a candidate.
        Computes score using all-or-nothing scoring mode.
        
        Payload:
        {
            "candidate_id": 123,
            "template_id": 456,
            "answers": [
                {"question_id": 1, "selected_option_ids": [1, 3]},
                {"question_id": 2, "selected_option_ids": [5]}
            ]
        }
        """
        # Validate input
        serializer = SubmitQuestionnaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        candidate_id = request.data.get('candidate_id')
        template_id = serializer.validated_data['template_id']
        answers = serializer.validated_data['answers']
        
        # Validate candidate exists
        try:
            candidate = Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {'error': f'Candidate with id {candidate_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate template exists
        try:
            template = QuestionnaireTemplate.objects.prefetch_related(
                'questions__options'
            ).get(id=template_id)
        except QuestionnaireTemplate.DoesNotExist:
            return Response(
                {'error': f'Template with id {template_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Compute score and save response
        try:
            with transaction.atomic():
                response = self._compute_and_save_response(
                    candidate, template, answers
                )
                # Update candidate status based on completion of all steps for this position
                position_key = template.position_key
                total_steps = QuestionnaireTemplate.objects.filter(
                    position_key=position_key, is_active=True
                ).count()
                completed_steps = (
                    CandidateQuestionnaireResponse.objects
                    .filter(candidate=candidate, position_key=position_key)
                    .values('template_id')
                    .distinct()
                    .count()
                )

                if total_steps > 0 and completed_steps < total_steps:
                    # Only set to incomplete if not already in a later stage
                    if candidate.status not in ['reviewing', 'shortlisted', 'interviewed', 'accepted', 'rejected']:
                        if candidate.status != 'incomplete':
                            candidate.status = 'incomplete'
                            candidate.save(update_fields=['status'])
                else:
                    # All steps completed: move to pending if not already in a later stage
                    if candidate.status not in ['reviewing', 'shortlisted', 'interviewed', 'accepted', 'rejected']:
                        if candidate.status != 'pending':
                            candidate.status = 'pending'
                            candidate.save(update_fields=['status'])
                response_serializer = CandidateQuestionnaireResponseSerializer(response)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _compute_and_save_response(self, candidate, template, answers):
        """
        Compute score using all-or-nothing mode and save response.
        Returns the created CandidateQuestionnaireResponse.
        """
        # Ensure idempotent per step (template) per candidate: replace existing response
        existing = CandidateQuestionnaireResponse.objects.filter(
            candidate=candidate, template=template
        ).first()
        if existing:
            # Delete previous selections and the response to avoid duplicates
            CandidateSelectedOption.objects.filter(response=existing).delete()
            existing.delete()
        # Build a map of question_id -> Question
        questions_map = {q.id: q for q in template.questions.all()}
        
        # Build a map of question_id -> set of correct option ids
        correct_answers_map = {}
        for question in template.questions.all():
            correct_options = set(
                opt.id for opt in question.options.all() if opt.is_correct
            )
            correct_answers_map[question.id] = correct_options
        
        # Validate all answers reference valid questions
        for answer in answers:
            question_id = answer['question_id']
            if question_id not in questions_map:
                raise ValueError(f'Question {question_id} not found in template')
        
        # Determine if this template is fully weighted (all questions use 'weighted')
        all_questions = list(template.questions.all())
        is_fully_weighted = all_questions and all(q.scoring_mode == 'weighted' for q in all_questions)

        # Compute score
        total_score = Decimal('0.00')
        if is_fully_weighted:
            # Max score is sum of per-question max option points
            max_score = Decimal('0.00')
            for q in all_questions:
                opts = list(q.options.all())
                if q.question_type == 'single_select':
                    q_max = max((opt.option_points or Decimal('0')) for opt in opts) if opts else Decimal('0')
                else:
                    q_max = sum((opt.option_points or Decimal('0')) for opt in opts)
                max_score += Decimal(q_max)
        else:
            max_score = template.get_total_points()
        
        # Create response object
        response = CandidateQuestionnaireResponse.objects.create(
            candidate=candidate,
            template=template,
            position_key=template.position_key,
            score=Decimal('0.00'),  # Will update after computing
            max_score=max_score
        )
        
        # Process each answer
        for answer in answers:
            question_id = answer['question_id']
            selected_option_ids = set(answer['selected_option_ids'])
            
            question = questions_map[question_id]
            correct_option_ids = correct_answers_map[question_id]
            
            # Validate selected options belong to this question
            valid_option_ids = set(opt.id for opt in question.options.all())
            invalid_selections = selected_option_ids - valid_option_ids
            if invalid_selections:
                raise ValueError(
                    f'Invalid option ids {invalid_selections} for question {question_id}'
                )
            
            # Save selected options
            for option_id in selected_option_ids:
                CandidateSelectedOption.objects.create(
                    response=response,
                    question_id=question_id,
                    option_id=option_id
                )
            
            # Compute score per question
            if is_fully_weighted and question.scoring_mode == 'weighted':
                # In fully weighted templates, add raw option_points to total_score
                if question.question_type == 'single_select':
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id:
                        selected_option = next((opt for opt in question.options.all() if opt.id == selected_id), None)
                        selected_points = (selected_option.option_points or Decimal('0')) if selected_option else Decimal('0')
                        total_score += Decimal(selected_points)
                else:
                    # Multi-select: sum the selected options' points
                    selected_points_sum = sum(
                        (opt.option_points or Decimal('0'))
                        for opt in question.options.all()
                        if opt.id in selected_option_ids
                    )
                    total_score += Decimal(selected_points_sum)

            elif question.scoring_mode == 'all_or_nothing':
                # Exact match required
                if selected_option_ids == correct_option_ids:
                    total_score += question.points
            elif question.scoring_mode == 'partial':
                if question.question_type == 'single_select':
                    # Single-select partial: score based on selected correct option points
                    # Only one selection is allowed by UI; use its points vs the max correct option points
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id and selected_id in correct_option_ids:
                        correct_options = [opt for opt in question.options.all() if opt.is_correct]
                        max_points = max((opt.option_points or Decimal('0')) for opt in correct_options) if correct_options else Decimal('0')
                        selected_points = next((opt.option_points or Decimal('0') for opt in correct_options if opt.id == selected_id), Decimal('0'))
                        if max_points and max_points > 0:
                            fraction = Decimal(selected_points) / Decimal(max_points)
                            if fraction < 0:
                                fraction = Decimal('0')
                            if fraction > 1:
                                fraction = Decimal('1')
                            total_score += (fraction * question.points)
                    # else: selected option not correct or no points -> 0
                else:
                    # Multi-select partial: normalize by total correct option_points
                    # Sum option_points for correct options
                    correct_options = [opt for opt in question.options.all() if opt.is_correct]
                    total_correct_points = sum((opt.option_points or Decimal('0')) for opt in correct_options)

                    if total_correct_points and total_correct_points > 0:
                        # Sum option_points for selected correct options
                        selected_correct_points = sum(
                            (opt.option_points or Decimal('0'))
                            for opt in correct_options
                            if opt.id in selected_option_ids
                        )
                        fraction = Decimal(selected_correct_points) / Decimal(total_correct_points)
                        if fraction < 0:
                            fraction = Decimal('0')
                        if fraction > 1:
                            fraction = Decimal('1')
                        total_score += (fraction * question.points)
                    else:
                        # No correct points configured -> contributes 0
                        pass
            elif question.scoring_mode == 'weighted':
                # Weighted scoring (non-fully-weighted template): original normalized-by-question points behavior
                # Useful for mixed templates where other questions still use question.points
                if question.question_type == 'single_select':
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id:
                        all_options = list(question.options.all())
                        max_points = max((opt.option_points or Decimal('0')) for opt in all_options) if all_options else Decimal('0')
                        selected_option = next((opt for opt in all_options if opt.id == selected_id), None)
                        selected_points = (selected_option.option_points or Decimal('0')) if selected_option else Decimal('0')
                        if max_points and max_points > 0:
                            fraction = Decimal(selected_points) / Decimal(max_points)
                            if fraction < 0:
                                fraction = Decimal('0')
                            if fraction > 1:
                                fraction = Decimal('1')
                            total_score += (fraction * question.points)
                else:
                    all_options = list(question.options.all())
                    total_option_points = sum((opt.option_points or Decimal('0')) for opt in all_options)

                    if total_option_points and total_option_points > 0:
                        selected_option_points = sum(
                            (opt.option_points or Decimal('0'))
                            for opt in all_options
                            if opt.id in selected_option_ids
                        )
                        fraction = Decimal(selected_option_points) / Decimal(total_option_points)
                        if fraction < 0:
                            fraction = Decimal('0')
                        if fraction > 1:
                            fraction = Decimal('1')
                        total_score += (fraction * question.points)
                    else:
                        pass
        
        # Update response with computed score
        response.score = total_score
        response.save()
        
        return response
    
    @action(detail=False, methods=['get'], url_path='analytics/by-position')
    def analytics_by_position(self, request):
        """
        Get analytics grouped by position.
        Returns average scores, response counts, etc.
        """
        position_key = request.query_params.get('position_key')
        
        queryset = self.get_queryset()
        if position_key:
            queryset = queryset.filter(position_key=position_key)
        
        # Aggregate stats
        stats = queryset.values('position_key', 'template__title').annotate(
            total_responses=Count('id'),
            avg_score=Avg('score'),
            avg_max_score=Avg('max_score'),
            avg_percentage=Avg(
                (100.0 * F('score')) / F('max_score')
            )
        ).order_by('position_key')
        
        return Response(list(stats))
    
    @action(detail=False, methods=['get'], url_path='analytics/option-distribution')
    def option_distribution(self, request):
        """
        Get distribution of selected options for a specific question.
        Query param: question_id (required)
        """
        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response(
                {'error': 'question_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get option selection counts
        selections = CandidateSelectedOption.objects.filter(
            question_id=question_id
        ).values(
            'option__id',
            'option__option_text',
            'option__is_correct'
        ).annotate(
            selection_count=Count('id')
        ).order_by('-selection_count')
        
        return Response(list(selections))


@api_view(['GET'])
@permission_classes([AllowAny])
def form_initialization(request):
    """
    Initialize the multi-step form.
    Returns available positions for Step 0.
    
    This is the entry point for the candidate application form.
    """
    # Read positions from JSON file
    positions_file = os.path.join(settings.BASE_DIR, 'positions.json')
    positions = []
    
    if os.path.exists(positions_file):
        try:
            with open(positions_file, 'r') as f:
                all_positions = json.load(f)
                # Filter only active positions
                positions = [p for p in all_positions if p.get('is_active', True)]
        except Exception as e:
            print(f"Error reading positions: {e}")
    
    # If no positions found, return defaults
    if not positions:
        positions = [
            {'id': 1, 'name': 'Pintor', 'is_active': True},
            {'id': 2, 'name': 'Auxiliar de Pintor', 'is_active': True},
            {'id': 3, 'name': 'Encarregado de Pintura', 'is_active': True},
        ]
    
    return Response({
        'step': 0,
        'step_name': 'position_selection',
        'title': 'Selecione o Cargo Pretendido',
        'description': 'Escolha a posição para a qual você deseja se candidatar',
        'positions': positions,
        'instructions': 'Após selecionar o cargo, você preencherá seus dados pessoais e responderá questionários específicos para a posição escolhida.'
    })
