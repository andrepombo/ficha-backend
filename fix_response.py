#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import CandidateQuestionnaireResponse, CandidateSelectedOption
from decimal import Decimal

# Get the response
response = CandidateQuestionnaireResponse.objects.get(id=6)
question = response.template.questions.first()

print(f'Response ID: {response.id}')
print(f'Question ID: {question.id}')
print(f'Current selected options: {response.selected_options.count()}')

# Get option 98 (1.00 pts)
option = question.options.get(id=98)
print(f'Option to select: {option.id} - {option.option_text[:50]} - {option.option_points} pts')

# Delete any existing selections for this question
CandidateSelectedOption.objects.filter(response=response, question=question).delete()

# Create the selected option
selected = CandidateSelectedOption.objects.create(
    response=response,
    question=question,
    option=option
)

print(f'✓ Created selected option ID: {selected.id}')

# Recalculate score
all_options = list(question.options.all())
max_points = max((opt.option_points or Decimal('0')) for opt in all_options)
selected_points = option.option_points or Decimal('0')
fraction = Decimal(selected_points) / Decimal(max_points)
response.score = fraction * question.points
response.save()

print(f'✓ Score updated: {response.score}/{response.max_score}')

# Verify
print(f'✓ New selected options count: {response.selected_options.count()}')
print(f'✓ Selected option IDs: {list(response.selected_options.values_list("option_id", flat=True))}')
