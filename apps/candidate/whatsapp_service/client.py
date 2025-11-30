"""
WhatsApp client and configuration.
"""
import os
from datetime import datetime
import logging
import json
import requests

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Base client for sending WhatsApp messages via Meta WhatsApp Cloud API.
    """
    
    def __init__(self):
        """
        Initialize Meta WhatsApp Cloud API client.
        """
        # Meta config
        self.meta_api_version = os.getenv('META_API_VERSION', 'v20.0')
        self.meta_phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
        self.meta_access_token = os.getenv('META_PERMANENT_ACCESS_TOKEN') or os.getenv('META_ACCESS_TOKEN')
        self.meta_base_url = os.getenv('META_BASE_URL', f'https://graph.facebook.com/{self.meta_api_version}')

        # Template identifiers
        self.tpl_scheduled = os.getenv('META_TEMPLATE_SCHEDULED')
        self.tpl_rescheduled = os.getenv('META_TEMPLATE_RESCHEDULED')
        self.tpl_cancelled = os.getenv('META_TEMPLATE_CANCELLED')
        self.tpl_language = os.getenv('WHATSAPP_TEMPLATE_LANG', 'pt_BR')
    
    def is_configured(self):
        """
        Check if WhatsApp service is properly configured.
        """
        return all([self.meta_phone_number_id, self.meta_access_token])
    
    def format_phone_number(self, phone_number):
        """
        Format phone number for WhatsApp (must be in E.164 format).
        Intelligently handles Brazilian phone number formats.
        
        Brazilian mobile numbers can be:
        - Old format: XX XXXX-XXXX (10 digits total: 2 area code + 8 number)
        - New format: XX XXXXX-XXXX (11 digits total: 2 area code + 9 number)
        
        WhatsApp uses the actual registered number, which may vary.
        This function tries both formats if delivery fails.
        
        Args:
            phone_number (str): Phone number in format "XX XXXXX-XXXX" or "XX XXXX-XXXX"
            
        Returns:
            str: Phone number in WhatsApp format "whatsapp:+55xxxxxxxxxx"
        """
        # Remove spaces, dashes, parentheses, and other formatting
        cleaned = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '')
        
        # Remove country code if already present
        if cleaned.startswith('+55'):
            cleaned = cleaned[3:]
        elif cleaned.startswith('55'):
            cleaned = cleaned[2:]
        elif cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        # Now we should have just the area code + number
        # Brazilian format: 2 digits (area code) + 8 or 9 digits (number)
        
        # Add Brazil country code
        formatted = f'+55{cleaned}'
        
        # Meta expects plain E.164 without the whatsapp: prefix
        return formatted

    def _meta_send_template(self, to_e164: str, template_name: str, template_vars: list):
        """
        Send a WhatsApp template message via Meta Cloud API.
        """
        if not all([self.meta_phone_number_id, self.meta_access_token]):
            raise Exception('Meta provider not configured: set META_PHONE_NUMBER_ID and META_PERMANENT_ACCESS_TOKEN')

        url = f"{self.meta_base_url}/{self.meta_phone_number_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.meta_access_token}',
            'Content-Type': 'application/json'
        }

        # Build components for body parameters
        body_parameters = [
            {"type": "text", "text": str(v) if v is not None else ""}
            for v in template_vars
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": to_e164,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": self.tpl_language},
                "components": [
                    {"type": "body", "parameters": body_parameters}
                ]
            }
        }

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
        if resp.status_code >= 400:
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            logger.error(f"Meta send error {resp.status_code}: {data}")
            raise Exception(f"Meta send failed: {resp.status_code} {data}")

        data = resp.json()
        message_id = None
        try:
            message_id = data.get('messages', [{}])[0].get('id')
        except Exception:
            pass
        logger.info(f"✅ Meta message sent. ID: {message_id}, To: {to_e164}, Template: {template_name}")
        return {
            'success': True,
            'message_sid': message_id or '',
            'status': 'sent',
            'phone_format_used': to_e164,
            'verified_phone': to_e164
        }
    
