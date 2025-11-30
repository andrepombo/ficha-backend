"""
WhatsApp webhook views for receiving incoming messages and status updates from Meta.
"""

import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os

logger = logging.getLogger(__name__)

# Webhook verify token - set this in your .env
WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'your_verify_token_here')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    """
    Handle WhatsApp webhook requests from Meta.
    
    GET: Webhook verification (Meta calls this to verify your endpoint)
    POST: Incoming messages and status updates
    """
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return HttpResponse(challenge, content_type='text/plain')
        else:
            logger.warning(f"Webhook verification failed. Token: {token}")
            return HttpResponse('Forbidden', status=403)
    
    elif request.method == 'POST':
        # Handle incoming webhook data
        try:
            body = json.loads(request.body.decode('utf-8'))
            logger.info(f"Webhook received: {json.dumps(body, indent=2)}")
            
            # Process webhook entries
            entries = body.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # Handle incoming messages
                    if 'messages' in value:
                        messages = value.get('messages', [])
                        for message in messages:
                            from_number = message.get('from')
                            message_type = message.get('type')
                            timestamp = message.get('timestamp')
                            
                            logger.info(f"Received message from {from_number}, type: {message_type}")
                            
                            # Extract message content based on type
                            if message_type == 'text':
                                text_body = message.get('text', {}).get('body', '')
                                logger.info(f"Text message: {text_body}")
                            
                            # Here you can:
                            # 1. Store the conversation in database
                            # 2. Mark candidate as "messaged" for WhatsApp eligibility
                            # 3. Auto-reply if needed
                            
                            # For now, just log it
                            logger.info(f"Message from {from_number} registered. They can now receive notifications.")
                    
                    # Handle message status updates (sent, delivered, read, failed)
                    if 'statuses' in value:
                        statuses = value.get('statuses', [])
                        for status in statuses:
                            message_id = status.get('id')
                            status_type = status.get('status')
                            timestamp = status.get('timestamp')
                            recipient = status.get('recipient_id')
                            
                            logger.info(f"Message {message_id} to {recipient}: {status_type}")
                            
                            # Here you can update Interview.whatsapp_status in database
            
            return JsonResponse({'status': 'success'}, status=200)
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return HttpResponse('Method not allowed', status=405)
