"""
Signals for automatic score recalculation when questions are updated.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Question, CandidateQuestionnaireResponse


@receiver(post_save, sender=Question)
def recalculate_scores_on_question_update(sender, instance, created, **kwargs):
    """
    Recalculate all response scores when a question is updated.
    This ensures scores stay accurate when question points or scoring mode changes.
    """
    if created:
        # Don't recalculate for new questions (no responses yet)
        return
    
    # Get all responses for this question's template
    responses = CandidateQuestionnaireResponse.objects.filter(
        template=instance.template
    )
    
    if not responses.exists():
        return
    
    print(f"🔄 Recalculating scores for {responses.count()} responses due to question update...")
    
    for response in responses:
        # Determine if the template is fully weighted
        questions = list(response.template.questions.all())
        is_fully_weighted = questions and all(q.scoring_mode == 'weighted' for q in questions)

        # Recalculate score for this response
        total_score = Decimal('0.00')

        for question in questions:
            # Get selected options for this question
            selected_options = response.selected_options.filter(question=question)
            selected_option_ids = set(selected_options.values_list('option_id', flat=True))
            
            if not selected_option_ids:
                continue
            
            # Get correct options
            correct_options = question.options.filter(is_correct=True)
            correct_option_ids = set(correct_options.values_list('id', flat=True))
            
            # Calculate score based on scoring mode
            if is_fully_weighted and question.scoring_mode == 'weighted':
                # Sum raw option_points for selected options
                if question.question_type == 'single_select':
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id:
                        selected_option = next((opt for opt in question.options.all() if opt.id == selected_id), None)
                        selected_points = (selected_option.option_points or Decimal('0')) if selected_option else Decimal('0')
                        total_score += Decimal(selected_points)
                else:
                    selected_points_sum = sum(
                        (opt.option_points or Decimal('0'))
                        for opt in question.options.all()
                        if opt.id in selected_option_ids
                    )
                    total_score += Decimal(selected_points_sum)

            elif question.scoring_mode == 'all_or_nothing':
                if selected_option_ids == correct_option_ids:
                    total_score += question.points
                    
            elif question.scoring_mode == 'partial':
                if question.question_type == 'single_select':
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id and selected_id in correct_option_ids:
                        correct_opts = list(question.options.filter(is_correct=True))
                        max_points = max((opt.option_points or Decimal('0')) for opt in correct_opts) if correct_opts else Decimal('0')
                        selected_points = next((opt.option_points or Decimal('0') for opt in correct_opts if opt.id == selected_id), Decimal('0'))
                        if max_points and max_points > 0:
                            fraction = Decimal(selected_points) / Decimal(max_points)
                            fraction = max(Decimal('0'), min(Decimal('1'), fraction))
                            total_score += (fraction * question.points)
                else:
                    # Multi-select partial
                    correct_opts = list(question.options.filter(is_correct=True))
                    total_correct_points = sum((opt.option_points or Decimal('0')) for opt in correct_opts)
                    if total_correct_points and total_correct_points > 0:
                        selected_correct_points = sum(
                            (opt.option_points or Decimal('0'))
                            for opt in correct_opts
                            if opt.id in selected_option_ids
                        )
                        fraction = Decimal(selected_correct_points) / Decimal(total_correct_points)
                        fraction = max(Decimal('0'), min(Decimal('1'), fraction))
                        total_score += (fraction * question.points)
                        
            elif question.scoring_mode == 'weighted':
                if question.question_type == 'single_select':
                    selected_id = next(iter(selected_option_ids), None)
                    if selected_id:
                        all_options = list(question.options.all())
                        max_points = max((opt.option_points or Decimal('0')) for opt in all_options) if all_options else Decimal('0')
                        selected_option = next((opt for opt in all_options if opt.id == selected_id), None)
                        selected_points = (selected_option.option_points or Decimal('0')) if selected_option else Decimal('0')
                        if max_points and max_points > 0:
                            fraction = Decimal(selected_points) / Decimal(max_points)
                            total_score += (fraction * question.points)
                else:
                    # Multi-select weighted
                    all_options = list(question.options.all())
                    total_option_points = sum((opt.option_points or Decimal('0')) for opt in all_options)
                    if total_option_points and total_option_points > 0:
                        selected_option_points = sum(
                            (opt.option_points or Decimal('0'))
                            for opt in all_options
                            if opt.id in selected_option_ids
                        )
                        fraction = Decimal(selected_option_points) / Decimal(total_option_points)
                        total_score += (fraction * question.points)
        
        # Compute max_score depending on mode
        if is_fully_weighted:
            max_score = Decimal('0.00')
            for q in questions:
                opts = list(q.options.all())
                if q.question_type == 'single_select':
                    q_max = max((opt.option_points or Decimal('0')) for opt in opts) if opts else Decimal('0')
                else:
                    q_max = sum((opt.option_points or Decimal('0')) for opt in opts)
                max_score += Decimal(q_max)
        else:
            max_score = response.template.get_total_points()

        # Update response score
        old_score = response.score
        response.score = total_score
        response.max_score = max_score
        response.save()
        
        print(f"  ✓ Response {response.id}: {old_score} → {total_score}/{response.max_score}")
