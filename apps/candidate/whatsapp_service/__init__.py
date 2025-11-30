"""
WhatsApp service package for sending interview notifications.

This package organizes WhatsApp functionality into separate modules:
- client.py: Base client and API configuration
- notifications.py: Interview notification services
"""

from .notifications import WhatsAppNotifications


class WhatsAppService(WhatsAppNotifications):
    """
    Main WhatsApp service that combines client and notification functionality.
    Maintains backward compatibility with the original single-file implementation.
    """
    pass


# Create a singleton instance for backward compatibility
whatsapp_service = WhatsAppService()

__all__ = [
    'WhatsAppService',
    'whatsapp_service',
    'WhatsAppNotifications',
]
