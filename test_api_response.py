#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.serializers import CandidateQuestionnaireResponseSerializer
from apps.candidate.models import CandidateQuestionnaireResponse, Candidate

# Get the candidate
candidate = Candidate.objects.filter(full_name__icontains='ANDRE').first()
if not candidate:
    print("Candidate not found")
    sys.exit(1)

print(f"Candidate: {candidate.full_name} (ID: {candidate.id})")

# Get responses for this candidate
responses = CandidateQuestionnaireResponse.objects.filter(candidate=candidate)
print(f"Found {responses.count()} responses")

for response in responses:
    print(f"\n{'='*60}")
    print(f"Response ID: {response.id}")
    print(f"Template: {response.template.title}")
    print(f"Score: {response.score}/{response.max_score}")
    
    # Serialize it
    serializer = CandidateQuestionnaireResponseSerializer(response)
    data = serializer.data
    
    print(f"Selected options in serialized data: {len(data.get('selected_options', []))}")
    for opt in data.get('selected_options', []):
        print(f"  - Question {opt['question']}: Option {opt['option']} - {opt['option_text']} - Correct: {opt['is_correct']}")
    
    # Check database
    print(f"Selected options in database: {response.selected_options.count()}")
    for sel in response.selected_options.all():
        print(f"  - Question {sel.question.id}: Option {sel.option.id} - {sel.option.option_text[:50]}")
