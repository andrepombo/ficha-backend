"""
WhatsApp notification services for interview management.
"""
from .client import WhatsAppClient, logger


class WhatsAppNotifications(WhatsAppClient):
    """Service for sending WhatsApp notifications about interviews."""
    
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

            to_number = candidate.phone_number
            to_e164 = self.format_phone_number(to_number)
            template_name = self.tpl_scheduled
            if not template_name:
                raise Exception('Set META_TEMPLATE_SCHEDULED')
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
            
            logger.info(
                f"WhatsApp message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
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
            
            # Note: Reminder messages would need a separate template in Meta
            # For now, returning not implemented
            logger.warning("Reminder messages not yet implemented for Meta provider")
            return {
                'success': False,
                'error': 'Reminder messages not yet implemented for Meta provider'
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

            to_number = candidate.phone_number
            to_e164 = self.format_phone_number(to_number)
            template_name = self.tpl_cancelled
            if not template_name:
                raise Exception('Set META_TEMPLATE_CANCELLED')
            template_vars = [
                candidate.full_name,
                interview.title,
                date_formatted,
                time_formatted
            ]
            result = self._meta_send_template(to_e164, template_name, template_vars)
            
            logger.info(
                f"WhatsApp cancellation message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
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

            to_number = candidate.phone_number
            to_e164 = self.format_phone_number(to_number)
            template_name = self.tpl_rescheduled
            if not template_name:
                raise Exception('Set META_TEMPLATE_RESCHEDULED')
            # Template has only 3 variables: {{1}}=name, {{2}}=date, {{3}}=time
            vars_list = [
                candidate.full_name,
                new_date_formatted,
                new_time_formatted
            ]
            result = self._meta_send_template(to_e164, template_name, vars_list)
            
            logger.info(
                f"WhatsApp rescheduling message sent successfully to {candidate.full_name}. "
                f"Message SID: {result['message_sid']}, Format used: {result.get('phone_format_used')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp rescheduling message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
