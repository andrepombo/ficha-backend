#!/usr/bin/env python
"""
Script to recalculate questionnaire scores for existing responses.
Useful when you change the scoring mode of a question.

Usage:
    python manage.py shell < utils/recalculate_questionnaire_scores.py
    
Or run specific response:
    python utils/recalculate_questionnaire_scores.py --response-id <id>
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from decimal import Decimal
from apps.candidate.models import CandidateQuestionnaireResponse, Question

def recalculate_response_score(response):
    """Recalculate the score for a single response."""
    print(f"\n{'='*60}")
    print(f"Recalculating response ID: {response.id}")
    print(f"Candidate: {response.candidate.full_name}")
    print(f"Template: {response.template.title}")
    print(f"Old score: {response.score}/{response.max_score}")
    
    template = response.template
    total_score = Decimal('0.00')
    max_score = template.get_total_points()
    
    # Get all questions for this template
    questions = template.questions.all()
    
    for question in questions:
        # Get selected options for this question
        selected_options = response.selected_options.filter(question=question)
        selected_option_ids = set(selected_options.values_list('option_id', flat=True))
        
        # Get correct options
        correct_options = question.options.filter(is_correct=True)
        correct_option_ids = set(correct_options.values_list('id', flat=True))
        
        print(f"\n  Question: {question.question_text[:60]}...")
        print(f"  Scoring mode: {question.scoring_mode}")
        print(f"  Selected options: {list(selected_option_ids)}")
        print(f"  Correct options: {list(correct_option_ids)}")
        
        # Compute score per question based on scoring mode
        question_score = Decimal('0.00')
        
        if question.scoring_mode == 'all_or_nothing':
            # Exact match required
            if selected_option_ids == correct_option_ids:
                question_score = question.points
                print(f"  ✓ All or nothing: MATCH - {question_score} points")
            else:
                print(f"  ✗ All or nothing: NO MATCH - 0 points")
                
        elif question.scoring_mode == 'partial':
            if question.question_type == 'single_select':
                selected_id = next(iter(selected_option_ids), None)
                if selected_id and selected_id in correct_option_ids:
                    correct_opts = list(question.options.filter(is_correct=True))
                    max_points = max((opt.option_points or Decimal('0')) for opt in correct_opts) if correct_opts else Decimal('0')
                    selected_points = next((opt.option_points or Decimal('0') for opt in correct_opts if opt.id == selected_id), Decimal('0'))
                    if max_points and max_points > 0:
                        fraction = Decimal(selected_points) / Decimal(max_points)
                        question_score = fraction * question.points
                        print(f"  ✓ Partial (single): {selected_points}/{max_points} = {fraction:.2f} × {question.points} = {question_score} points")
                    else:
                        print(f"  ✗ Partial (single): No max points configured")
                else:
                    print(f"  ✗ Partial (single): Selected option not correct")
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
                    question_score = fraction * question.points
                    print(f"  ✓ Partial (multi): {selected_correct_points}/{total_correct_points} = {fraction:.2f} × {question.points} = {question_score} points")
                else:
                    print(f"  ✗ Partial (multi): No correct points configured")
                    
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
                        question_score = fraction * question.points
                        print(f"  ✓ Weighted (single): {selected_points}/{max_points} = {fraction:.2f} × {question.points} = {question_score} points")
                    else:
                        print(f"  ✗ Weighted (single): No max points configured")
                else:
                    print(f"  ✗ Weighted (single): No option selected")
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
                    question_score = fraction * question.points
                    print(f"  ✓ Weighted (multi): {selected_option_points}/{total_option_points} = {fraction:.2f} × {question.points} = {question_score} points")
                else:
                    print(f"  ✗ Weighted (multi): No option points configured")
        
        total_score += question_score
    
    # Update response
    response.score = total_score
    response.max_score = max_score
    response.save()
    
    print(f"\n  New score: {response.score}/{response.max_score}")
    print(f"  Percentage: {response.get_percentage():.1f}%")
    print(f"{'='*60}\n")
    
    return response

def recalculate_all_responses():
    """Recalculate scores for all responses."""
    responses = CandidateQuestionnaireResponse.objects.all()
    print(f"Found {responses.count()} responses to recalculate")
    
    for response in responses:
        try:
            recalculate_response_score(response)
        except Exception as e:
            print(f"ERROR recalculating response {response.id}: {e}")
            import traceback
            traceback.print_exc()

def recalculate_by_template(template_id):
    """Recalculate scores for all responses to a specific template."""
    responses = CandidateQuestionnaireResponse.objects.filter(template_id=template_id)
    print(f"Found {responses.count()} responses for template {template_id}")
    
    for response in responses:
        try:
            recalculate_response_score(response)
        except Exception as e:
            print(f"ERROR recalculating response {response.id}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Recalculate questionnaire scores')
    parser.add_argument('--response-id', type=int, help='Recalculate specific response')
    parser.add_argument('--template-id', type=int, help='Recalculate all responses for a template')
    parser.add_argument('--all', action='store_true', help='Recalculate all responses')
    
    args = parser.parse_args()
    
    if args.response_id:
        response = CandidateQuestionnaireResponse.objects.get(id=args.response_id)
        recalculate_response_score(response)
    elif args.template_id:
        recalculate_by_template(args.template_id)
    elif args.all:
        recalculate_all_responses()
    else:
        print("Please specify --response-id, --template-id, or --all")
        parser.print_help()
