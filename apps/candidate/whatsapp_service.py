"""
WhatsApp notification service.
Supports Twilio API and Meta WhatsApp Cloud API (provider switchable via env).
"""
import os
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
import json
import requests

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service class for sending WhatsApp messages via Twilio.
    """
    
    def __init__(self):
        """
        Initialize provider-specific clients based on environment.
        """
        self.provider = (os.getenv('WHATSAPP_PROVIDER') or 'twilio').lower()

        # Twilio config
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM')
        self.status_callback_url = os.getenv('TWILIO_STATUS_CALLBACK_URL')

        # Meta config
        self.meta_api_version = os.getenv('META_API_VERSION', 'v20.0')
        self.meta_phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
        self.meta_access_token = os.getenv('META_PERMANENT_ACCESS_TOKEN') or os.getenv('META_ACCESS_TOKEN')
        self.meta_base_url = os.getenv('META_BASE_URL', f'https://graph.facebook.com/{self.meta_api_version}')

        # Template identifiers (either Content SIDs for Twilio or names for Meta)
        self.tpl_scheduled = os.getenv('TWILIO_CONTENT_SID_SCHEDULED') or os.getenv('META_TEMPLATE_SCHEDULED')
        self.tpl_rescheduled = os.getenv('TWILIO_CONTENT_SID_RESCHEDULED') or os.getenv('META_TEMPLATE_RESCHEDULED')
        self.tpl_cancelled = os.getenv('TWILIO_CONTENT_SID_CANCELLED') or os.getenv('META_TEMPLATE_CANCELLED')
        self.tpl_language = os.getenv('WHATSAPP_TEMPLATE_LANG', 'pt_BR')

        # Twilio client (only if provider is twilio)
        if self.provider == 'twilio':
            if not all([self.account_sid, self.auth_token, self.whatsapp_from]):
                logger.warning(
                    "WhatsApp Twilio provider not configured. Set TWILIO_ACCOUNT_SID, "
                    "TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM."
                )
                self.client = None
            else:
                self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def is_configured(self):
        """
        Check if WhatsApp service is properly configured for the selected provider.
        """
        if self.provider == 'twilio':
            return self.client is not None
        # Meta provider
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
        
        if self.provider == 'twilio':
            return f'whatsapp:{formatted}'
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
    
    def _try_send_message(self, candidate, message_body):
        """
        Internal method to send a WhatsApp message with retry logic for different number formats.
        Automatically saves the working phone format to candidate.whatsapp_phone for future use.
        
        For new candidates (no saved whatsapp_phone), tries both formats:
        1. Original format (as entered in database)
        2. Alternative format (with/without leading 9)
        
        Args:
            candidate: Candidate model instance
            message_body: Message content
            
        Returns:
            dict: Response with success status and message SID or error
        """
        # First, try using the saved whatsapp_phone if available
        if candidate.whatsapp_phone:
            saved_phone = candidate.whatsapp_phone
            logger.info(f"Using saved WhatsApp phone format: {saved_phone}")
            formatted_number = self.format_phone_number(saved_phone)
            
            try:
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.whatsapp_from,
                    to=formatted_number
                )
                logger.info(f"✅ Message sent with saved format. SID: {message.sid}, Status: {message.status}, To: {formatted_number}")
                
                # Log delivery status for debugging
                if hasattr(message, 'error_code') and message.error_code:
                    logger.warning(f"⚠️ Message has error code: {message.error_code} - {message.error_message}")
                
                return {
                    'success': True,
                    'message_sid': message.sid,
                    'status': message.status,
                    'phone_format_used': formatted_number,
                    'verified_phone': saved_phone
                }
            except TwilioRestException as e:
                logger.warning(f"Saved WhatsApp phone failed (Error {e.code}), trying alternatives: {e}")
                # Continue to try other formats
        
        # Try sending with the phone number
        # For area code 85, prioritize 8-digit format (without leading 9)
        to_number = candidate.phone_number
        cleaned = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Determine which format to try first
        primary_number = to_number
        alternative_number = None
        
        # If it's an 11-digit number (area code + 9 + 8 digits)
        if len(cleaned) == 11 and cleaned[2] == '9':
            # Keep original 9-digit format as primary for all area codes
            primary_number = to_number
            # Alternative: 8-digit format (without 9)
            alternative_number = f"{cleaned[:2]} {cleaned[3:7]}-{cleaned[7:]}"
            logger.info(f"11-digit number detected: trying 9-digit format first, then 8-digit")
        elif len(cleaned) == 10:
            # 10-digit number (area code + 8 digits)
            # Primary: try with 9 first (modern mobile format)
            primary_number = f"{cleaned[:2]} 9{cleaned[2:6]}-{cleaned[6:]}"
            # Alternative: keep 8-digit format
            alternative_number = to_number
            logger.info(f"10-digit number detected: trying 9-digit format first, then 8-digit")
        
        # Try primary format
        formatted_number = self.format_phone_number(primary_number)
        logger.info(f"📱 Attempting to send to primary format: {formatted_number}")

        if self.provider == 'twilio':
            try:
                create_kwargs = {
                    'from_': self.whatsapp_from,
                    'to': formatted_number
                }
                if self.status_callback_url:
                    create_kwargs['status_callback'] = self.status_callback_url
                # Freeform body for Twilio path (kept for backward compatibility)
                create_kwargs['body'] = message_body

                message = self.client.messages.create(**create_kwargs)

                logger.info(f"✅ Message sent with primary format. SID: {message.sid}, Status: {message.status}, To: {formatted_number}")

                if hasattr(message, 'error_code') and message.error_code:
                    logger.warning(f"⚠️ Message has error code: {message.error_code} - {message.error_message}")

                if not candidate.whatsapp_phone or candidate.whatsapp_phone != primary_number:
                    candidate.whatsapp_phone = primary_number
                    candidate.save(update_fields=['whatsapp_phone'])
                    logger.info(f"💾 Saved working WhatsApp format: {primary_number}")

                return {
                    'success': True,
                    'message_sid': message.sid,
                    'status': message.status,
                    'phone_format_used': formatted_number,
                    'verified_phone': primary_number
                }
            except TwilioRestException as e:
                if e.code in [63015, 21211] and alternative_number:
                    logger.warning(f"Failed with {formatted_number}, trying alternative format")
                    alternative_formatted = self.format_phone_number(alternative_number)
                    logger.info(f"🔄 Trying alternative format: {alternative_formatted}")
                    try:
                        create_kwargs = {
                            'from_': self.whatsapp_from,
                            'to': alternative_formatted,
                            'body': message_body
                        }
                        if self.status_callback_url:
                            create_kwargs['status_callback'] = self.status_callback_url
                        message = self.client.messages.create(**create_kwargs)
                        logger.info(f"✅ Message sent with alternative format. SID: {message.sid}, Status: {message.status}, To: {alternative_formatted}")
                        if hasattr(message, 'error_code') and message.error_code:
                            logger.warning(f"⚠️ Message has error code: {message.error_code} - {message.error_message}")
                        candidate.whatsapp_phone = alternative_number
                        candidate.save(update_fields=['whatsapp_phone'])
                        logger.info(f"💾 Saved working WhatsApp format (alternative): {alternative_number}")
                        return {
                            'success': True,
                            'message_sid': message.sid,
                            'status': message.status,
                            'phone_format_used': alternative_formatted,
                            'verified_phone': alternative_number
                        }
                    except TwilioRestException:
                        raise e
                else:
                    raise e
        else:
            # Meta provider: expect message_body already composed by caller for session messages.
            # For generic freeform (session window) not used; for templates we call _meta_send_template outside.
            # Here, just return an error to indicate template path should be used by caller methods.
            raise Exception('Meta provider requires template sending path in specific send_* methods')
    
    def send_interview_scheduled_message(self, interview):
        """
        Send WhatsApp message to candidate when interview is scheduled.
        
        Args:
            interview: Interview model instance
            
        Returns:
            dict: Response with success status and message SID or error
        """
        if not self.is_configured():
            logger.error("WhatsApp service is not configured")
            return {
                'success': False,
                'error': 'WhatsApp service not configured'
            }
        
        try:
            candidate = interview.candidate
            
            # Check if candidate has opted in to WhatsApp notifications
            if not candidate.whatsapp_opt_in:
                logger.info(f"Candidate {candidate.full_name} has not opted in to WhatsApp notifications. Skipping.")
                return {
                    'success': False,
                    'error': 'Candidate has not opted in to WhatsApp notifications',
                    'opt_in_required': True
                }
            date_formatted = interview.scheduled_date.strftime('%d/%m/%Y')
            time_formatted = interview.scheduled_time.strftime('%H:%M')
            interview_type_display = dict(interview.TYPE_CHOICES).get(
                interview.interview_type,
                interview.interview_type
            )

            if self.provider == 'meta':
                # Use Meta template
                to_number = candidate.whatsapp_phone or candidate.phone_number
                to_e164 = self.format_phone_number(to_number)
                template_name = os.getenv('META_TEMPLATE_SCHEDULED') or (self.tpl_scheduled if self.tpl_scheduled and not self.tpl_scheduled.startswith('H') else None)
                if not template_name:
                    raise Exception('Set META_TEMPLATE_SCHEDULED for Meta provider')
                template_vars = [
                    candidate.full_name,
                    interview.title,
                    interview_type_display,
                    date_formatted,
                    time_formatted,
                    str(interview.duration_minutes),
                    interview.location or ''
                ]
                result = self._meta_send_template(to_e164, template_name, template_vars)
            else:
                # Build freeform body for Twilio (session or template fallback configured elsewhere)
                message_body = f"""🎯 *Entrevista Agendada - Pinte Pinturas*

Olá {candidate.full_name}! 👋

Sua entrevista foi agendada com sucesso! ✅

📋 *Detalhes da Entrevista:*
• *Título:* {interview.title}
• *Tipo:* {interview_type_display}
• *Data:* {date_formatted}
• *Horário:* {time_formatted}
• *Duração:* {interview.duration_minutes} minutos"""

                if interview.location:
                    if interview.interview_type == 'video':
                        message_body += f"\n• *Link da reunião:* {interview.location}"
                    else:
                        message_body += f"\n• *Local:* {interview.location}"
                if interview.description:
                    message_body += f"\n\n📝 *Informações adicionais:*\n{interview.description}"
                message_body += "\n\n⏰ Por favor, chegue com 10 minutos de antecedência."
                message_body += "\n\n💼 Boa sorte! Estamos ansiosos para conhecê-lo(a)!"
                message_body += "\n\n_Pinte Pinturas - Equipe de RH_"
                result = self._try_send_message(candidate, message_body)
            
            logger.info(
                f"WhatsApp message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_interview_reminder_message(self, interview):
        """
        Send WhatsApp reminder message to candidate (e.g., 24 hours before interview).
        
        Args:
            interview: Interview model instance
            
        Returns:
            dict: Response with success status and message SID or error
        """
        if not self.is_configured():
            logger.error("WhatsApp service is not configured")
            return {
                'success': False,
                'error': 'WhatsApp service not configured'
            }
        
        try:
            candidate = interview.candidate
            
            # Check if candidate has opted in to WhatsApp notifications
            if not candidate.whatsapp_opt_in:
                logger.info(f"Candidate {candidate.full_name} has not opted in to WhatsApp notifications. Skipping.")
                return {
                    'success': False,
                    'error': 'Candidate has not opted in to WhatsApp notifications',
                    'opt_in_required': True
                }
            
            # Format the date and time
            date_formatted = interview.scheduled_date.strftime('%d/%m/%Y')
            time_formatted = interview.scheduled_time.strftime('%H:%M')
            
            # Build reminder message
            message_body = f"""⏰ *Lembrete de Entrevista - Pinte Pinturas*

Olá {candidate.full_name}! 👋

Este é um lembrete sobre sua entrevista agendada:

📋 *Detalhes:*
• *Título:* {interview.title}
• *Data:* {date_formatted}
• *Horário:* {time_formatted}"""

            # Add location/link if available
            if interview.location:
                if interview.interview_type == 'video':
                    message_body += f"\n• *Link:* {interview.location}"
                else:
                    message_body += f"\n• *Local:* {interview.location}"
            
            message_body += "\n\n✅ Confirme sua presença ou entre em contato caso precise reagendar."
            message_body += "\n\n_Pinte Pinturas - Equipe de RH_"
            
            # Send message with automatic retry for different phone formats
            result = self._try_send_message(candidate, message_body)
            
            logger.info(
                f"WhatsApp reminder sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp reminder: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp reminder: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_interview_cancelled_message(self, interview):
        """
        Send WhatsApp message to candidate when interview is cancelled.
        
        Args:
            interview: Interview model instance
            
        Returns:
            dict: Response with success status and message SID or error
        """
        if not self.is_configured():
            logger.error("WhatsApp service is not configured")
            return {
                'success': False,
                'error': 'WhatsApp service not configured'
            }
        
        try:
            candidate = interview.candidate
            
            # Check if candidate has opted in to WhatsApp notifications
            if not candidate.whatsapp_opt_in:
                logger.info(f"Candidate {candidate.full_name} has not opted in to WhatsApp notifications. Skipping.")
                return {
                    'success': False,
                    'error': 'Candidate has not opted in to WhatsApp notifications',
                    'opt_in_required': True
                }
            date_formatted = interview.scheduled_date.strftime('%d/%m/%Y')
            time_formatted = interview.scheduled_time.strftime('%H:%M')

            if self.provider == 'meta':
                to_number = candidate.whatsapp_phone or candidate.phone_number
                to_e164 = self.format_phone_number(to_number)
                template_name = os.getenv('META_TEMPLATE_CANCELLED') or (self.tpl_cancelled if self.tpl_cancelled and not self.tpl_cancelled.startswith('H') else None)
                if not template_name:
                    raise Exception('Set META_TEMPLATE_CANCELLED for Meta provider')
                template_vars = [
                    candidate.full_name,
                    interview.title,
                    date_formatted,
                    time_formatted
                ]
                result = self._meta_send_template(to_e164, template_name, template_vars)
            else:
                message_body = f"""❌ *Entrevista Cancelada - Pinte Pinturas*

Olá {candidate.full_name},

Informamos que a entrevista agendada foi cancelada:

📋 *Detalhes:*
• *Título:* {interview.title}
• *Data:* {date_formatted}
• *Horário:* {time_formatted}

Entraremos em contato em breve para reagendar.

Agradecemos sua compreensão.

_Pinte Pinturas - Equipe de RH_"""
                result = self._try_send_message(candidate, message_body)
            
            logger.info(
                f"WhatsApp cancellation message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp cancellation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp cancellation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_interview_rescheduled_message(self, interview, old_date=None, old_time=None):
        """
        Send WhatsApp message to candidate when interview is rescheduled.
        
        Args:
            interview: Interview model instance
            old_date: Previous scheduled date (optional)
            old_time: Previous scheduled time (optional)
            
        Returns:
            dict: Response with success status and message SID or error
        """
        if not self.is_configured():
            logger.error("WhatsApp service is not configured")
            return {
                'success': False,
                'error': 'WhatsApp service not configured'
            }
        
        try:
            candidate = interview.candidate
            
            # Check if candidate has opted in to WhatsApp notifications
            if not candidate.whatsapp_opt_in:
                logger.info(f"Candidate {candidate.full_name} has not opted in to WhatsApp notifications. Skipping.")
                return {
                    'success': False,
                    'error': 'Candidate has not opted in to WhatsApp notifications',
                    'opt_in_required': True
                }
            new_date_formatted = interview.scheduled_date.strftime('%d/%m/%Y')
            new_time_formatted = interview.scheduled_time.strftime('%H:%M')

            if self.provider == 'meta':
                to_number = candidate.whatsapp_phone or candidate.phone_number
                to_e164 = self.format_phone_number(to_number)
                template_name = os.getenv('META_TEMPLATE_RESCHEDULED') or (self.tpl_rescheduled if self.tpl_rescheduled and not self.tpl_rescheduled.startswith('H') else None)
                if not template_name:
                    raise Exception('Set META_TEMPLATE_RESCHEDULED for Meta provider')
                # Template has only 3 variables: {{1}}=name, {{2}}=date, {{3}}=time
                vars_list = [
                    candidate.full_name,
                    new_date_formatted,
                    new_time_formatted
                ]
                result = self._meta_send_template(to_e164, template_name, vars_list)
            else:
                message_body = f"""🔄 *Entrevista Reagendada - Pinte Pinturas*

Olá {candidate.full_name}!

Sua entrevista foi reagendada:"""
                if old_date and old_time:
                    old_date_formatted = old_date.strftime('%d/%m/%Y')
                    old_time_formatted = old_time.strftime('%H:%M')
                    message_body += f"\n\n❌ *Data anterior:*\n• {old_date_formatted} às {old_time_formatted}"
                message_body += f"""

✅ *Nova data:*
• *Data:* {new_date_formatted}
• *Horário:* {new_time_formatted}
• *Título:* {interview.title}"""
                if interview.location:
                    if interview.interview_type == 'video':
                        message_body += f"\n• *Link:* {interview.location}"
                    else:
                        message_body += f"\n• *Local:* {interview.location}"
                message_body += "\n\nAgradecemos sua compreensão!"
                message_body += "\n\n_Pinte Pinturas - Equipe de RH_"
                result = self._try_send_message(candidate, message_body)
            
            logger.info(
                f"WhatsApp rescheduling message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp rescheduling message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp rescheduling message: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Create a singleton instance
whatsapp_service = WhatsAppService()
