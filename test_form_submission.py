#!/usr/bin/env python
"""
Test script to simulate form submission and identify the 500 error.
Run with: python test_form_submission.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from apps.candidate.views import application_form_view
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

def test_form_submission():
    """Test form submission with questionnaire data"""
    factory = RequestFactory()
    
    # Create a POST request with sample data
    post_data = {
        'full_name': 'Test Candidate',
        'cpf': '123.456.789-00',
        'phone_number': '(11) 98765-4321',
        'email': 'test@example.com',
        'position_applied': 'Pintor',
        'has_own_transportation': 'True',
        'questionnaire_answers': '[{"template_id": 1, "answers": [{"question_id": 1, "selected_option_ids": [1]}]}]',
        'experiences-TOTAL_FORMS': '0',
        'experiences-INITIAL_FORMS': '0',
        'experiences-MIN_NUM_FORMS': '0',
        'experiences-MAX_NUM_FORMS': '1000',
    }
    
    request = factory.post('/form/', data=post_data)
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session['selected_position'] = 'Pintor'
    request.session.save()
    
    # Add messages
    msg_middleware = MessageMiddleware(lambda x: None)
    msg_middleware.process_request(request)
    
    print("=" * 80)
    print("Testing form submission...")
    print("=" * 80)
    
    try:
        response = application_form_view(request)
        print(f"\nResponse status code: {response.status_code}")
        print(f"Response type: {type(response)}")
        if hasattr(response, 'url'):
            print(f"Redirect URL: {response.url}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)

if __name__ == '__main__':
    test_form_submission()
