#!/usr/bin/env python
"""
Test script to create a weighted scoring questionnaire submission
and verify the color coding logic works correctly.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import (
    Candidate, QuestionnaireTemplate, Question, QuestionOption,
    CandidateQuestionnaireResponse, CandidateSelectedOption
)
from decimal import Decimal

print("="*70)
print("WEIGHTED SCORING TEST")
print("="*70)

# Find the Cultural questionnaire
try:
    template = QuestionnaireTemplate.objects.get(title='Cultural')
    print(f"\n✓ Found template: {template.title}")
except QuestionnaireTemplate.DoesNotExist:
    print("\n✗ Cultural template not found")
    sys.exit(1)

# Get the question
question = template.questions.first()
if not question:
    print("✗ No questions found in template")
    sys.exit(1)

print(f"✓ Question: {question.question_text[:60]}...")
print(f"  - Type: {question.question_type}")
print(f"  - Scoring mode: {question.scoring_mode}")
print(f"  - Points: {question.points}")

# Get all options
options = list(question.options.all().order_by('order'))
print(f"\n✓ Options ({len(options)}):")
for opt in options:
    print(f"  {opt.order}. {opt.option_text[:50]}... - {opt.option_points} pts")

if not options:
    print("✗ No options found")
    sys.exit(1)

# Find max points
max_points = max((opt.option_points or Decimal('0')) for opt in options)
print(f"\n✓ Max option points: {max_points}")

# Find or create a test candidate
candidate = Candidate.objects.filter(full_name__icontains='ANDRE').first()
if not candidate:
    print("\n✗ No candidate found")
    sys.exit(1)

print(f"\n✓ Candidate: {candidate.full_name} (ID: {candidate.id})")

# Delete existing response for this candidate and template
existing = CandidateQuestionnaireResponse.objects.filter(
    candidate=candidate,
    template=template
)
if existing.exists():
    print(f"\n⚠ Deleting {existing.count()} existing response(s)...")
    existing.delete()

# Create new response
response = CandidateQuestionnaireResponse.objects.create(
    candidate=candidate,
    template=template,
    score=Decimal('0'),
    max_score=template.get_total_points()
)
print(f"\n✓ Created response ID: {response.id}")

# Test all three scenarios
print("\n" + "="*70)
print("TESTING COLOR SCENARIOS")
print("="*70)

for test_option in options:
    print(f"\n--- Scenario: Candidate selects '{test_option.option_text[:40]}...' ({test_option.option_points} pts) ---")
    
    # Clear previous selections
    CandidateSelectedOption.objects.filter(response=response).delete()
    
    # Create selection
    selection = CandidateSelectedOption.objects.create(
        response=response,
        question=question,
        option=test_option
    )
    
    # Calculate score
    selected_points = test_option.option_points or Decimal('0')
    if max_points > 0:
        fraction = Decimal(selected_points) / Decimal(max_points)
        score = fraction * question.points
    else:
        score = Decimal('0')
    
    response.score = score
    response.save()
    
    # Determine color (same logic as frontend)
    if selected_points == 0:
        color = 'RED'
        icon = '🔴'
    elif selected_points == max_points:
        color = 'GREEN'
        icon = '🟢'
    else:
        color = 'YELLOW'
        icon = '🟡'
    
    print(f"  Selected points: {selected_points}")
    print(f"  Max points: {max_points}")
    print(f"  Score: {score}/{question.points} ({fraction*100:.1f}%)")
    print(f"  Color: {icon} {color}")
    
    # Verify in database
    saved_selections = response.selected_options.count()
    print(f"  ✓ Saved selections in DB: {saved_selections}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print(f"\nFinal response ID: {response.id}")
print(f"Selected option: {test_option.option_text[:50]}...")
print(f"Score: {response.score}/{response.max_score}")
print(f"\nNow check the candidate detail page in the browser!")
print(f"It should show {icon} {color} for this answer.")
