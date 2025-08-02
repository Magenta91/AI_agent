import os
import logging
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class MessageSender:
    def __init__(self, gmail_user: str, gmail_password: str, 
                 twilio_sid: str, twilio_token: str, twilio_whatsapp_number: str):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.twilio_client = Client(twilio_sid, twilio_token)
        self.twilio_whatsapp_number = twilio_whatsapp_number
        
    def send_message(self, lead: Dict, message: str, test_mode: bool = False) -> Tuple[bool, str]:
        """Send message via email or WhatsApp based on contact format."""
        if test_mode:
            logger.info(f"TEST MODE: Would send to {lead['name']} ({lead['contact']})")
            logger.info(f"Message: {message}")
            return True, "Test mode - message not actually sent"
        
        contact = lead['contact'].strip()
        
        # Determine if contact is email or phone number
        if self._is_email(contact):
            return self._send_email(lead, message, contact)
        elif self._is_phone_number(contact):
            return self._send_whatsapp(lead, message, contact)
        else:
            error_msg = f"Invalid contact format for {lead['name']}: {contact}"
            logger.error(error_msg)
            return False, error_msg
    
    def _is_email(self, contact: str) -> bool:
        """Check if contact is a valid email address."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, contact) is not None
    
    def _is_phone_number(self, contact: str) -> bool:
        """Check if contact is a valid phone number (basic check)."""
        # Remove common phone number characters
        cleaned = re.sub(r'[\s\-\(\)\+]', '', contact)
        # Check if it's all digits and reasonable length
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    def _send_email(self, lead: Dict, message: str, email: str) -> Tuple[bool, str]:
        """Send message via Gmail SMTP."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = email
            msg['Subject'] = f"Hello {lead['name']}!"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.gmail_user, email, text)
            server.quit()
            
            success_msg = f"Email sent successfully to {lead['name']} ({email})"
            logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Failed to send email to {lead['name']} ({email}): {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _send_whatsapp(self, lead: Dict, message: str, phone: str) -> Tuple[bool, str]:
        """Send message via Twilio WhatsApp API."""
        try:
            # Format phone number for WhatsApp
            if not phone.startswith('+'):
                # Clean the phone number
                cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
                
                # Indian numbers: if starts with 91 and is 12 digits, add +
                if cleaned_phone.startswith('91') and len(cleaned_phone) == 12:
                    phone = '+' + cleaned_phone
                # Indian numbers: if 10 digits and starts with 6,7,8,9 (Indian mobile prefixes)
                elif len(cleaned_phone) == 10 and cleaned_phone[0] in ['6', '7', '8', '9']:
                    phone = '+91' + cleaned_phone
                # US numbers: if 10 digits and starts with other digits
                elif len(cleaned_phone) == 10:
                    phone = '+1' + cleaned_phone
                # Otherwise, assume it needs + prefix
                else:
                    phone = '+' + cleaned_phone
            
            whatsapp_to = f"whatsapp:{phone}"
            
            # Send WhatsApp message
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_whatsapp_number,
                to=whatsapp_to
            )
            
            success_msg = f"WhatsApp sent successfully to {lead['name']} ({phone})"
            logger.info(success_msg)
            return True, success_msg
            
        except TwilioException as e:
            error_msg = f"Failed to send WhatsApp to {lead['name']} ({phone}): {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending WhatsApp to {lead['name']} ({phone}): {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def test_connection(self) -> Dict[str, bool]:
        """Test both email and WhatsApp connections."""
        results = {}
        
        # Test Gmail connection
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.quit()
            results['gmail'] = True
            logger.info("Gmail connection test successful")
        except Exception as e:
            results['gmail'] = False
            logger.error(f"Gmail connection test failed: {e}")
        
        # Test Twilio connection
        try:
            # Try to fetch account info to test connection
            account = self.twilio_client.api.accounts(self.twilio_client.account_sid).fetch()
            results['twilio'] = True
            logger.info("Twilio connection test successful")
        except Exception as e:
            results['twilio'] = False
            logger.error(f"Twilio connection test failed: {e}")
        
        return results