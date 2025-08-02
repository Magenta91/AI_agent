#!/usr/bin/env python3
"""
Outreach Assistant - Automated lead outreach via email and WhatsApp
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from typing import List, Dict

from google_sheets import GoogleSheetsManager
from message_generator import MessageGenerator
from sender import MessageSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('outreach_assistant.log')
    ]
)

logger = logging.getLogger(__name__)

class OutreachAssistant:
    def __init__(self):
        self.sheets_manager = None
        self.message_generator = None
        self.sender = None
        self._load_environment()
        self._initialize_components()
    
    def _load_environment(self):
        """Load environment variables from .env file."""
        load_dotenv()
        
        # Required environment variables
        required_vars = [
            'GOOGLE_SHEETS_CREDENTIALS',
            'SPREADSHEET_ID',
            'GEMINI_API_KEY',
            'GMAIL_USER',
            'GMAIL_APP_PASSWORD',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_WHATSAPP_NUMBER'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file and ensure all variables are set.")
            sys.exit(1)
        
        logger.info("Environment variables loaded successfully")
    
    def _initialize_components(self):
        """Initialize all components with environment variables."""
        try:
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager(
                credentials_path=os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
                spreadsheet_id=os.getenv('SPREADSHEET_ID')
            )
            
            # Initialize message generator
            self.message_generator = MessageGenerator(
                api_key=os.getenv('GEMINI_API_KEY')
            )
            
            # Initialize message sender
            self.sender = MessageSender(
                gmail_user=os.getenv('GMAIL_USER'),
                gmail_password=os.getenv('GMAIL_APP_PASSWORD'),
                twilio_sid=os.getenv('TWILIO_ACCOUNT_SID'),
                twilio_token=os.getenv('TWILIO_AUTH_TOKEN'),
                twilio_whatsapp_number=os.getenv('TWILIO_WHATSAPP_NUMBER')
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            sys.exit(1)
    
    def run_outreach_campaign(self, test_mode: bool = False, sheet_name: str = "outreach_leads"):
        """Run the main outreach campaign."""
        logger.info(f"Starting outreach campaign (test_mode={test_mode})")
        
        try:
            # Get pending leads
            pending_leads = self.sheets_manager.get_pending_leads(sheet_name)
            
            if not pending_leads:
                logger.info("No pending leads found. Campaign complete.")
                return
            
            logger.info(f"Processing {len(pending_leads)} pending leads...")
            
            success_count = 0
            error_count = 0
            
            for lead in pending_leads:
                logger.info(f"Processing lead: {lead['name']} ({lead['contact']})")
                
                # Generate personalized message
                message = self.message_generator.generate_message(lead)
                if not message:
                    logger.error(f"Failed to generate message for {lead['name']}")
                    if not test_mode:
                        self.sheets_manager.update_lead_status(lead['row_number'], "Error")
                    error_count += 1
                    continue
                
                # Send message
                success, result_msg = self.sender.send_message(lead, message, test_mode)
                
                if success:
                    logger.info(f"SUCCESS: {result_msg}")
                    if not test_mode:
                        self.sheets_manager.update_lead_status(lead['row_number'], "Sent")
                    success_count += 1
                else:
                    logger.error(f"ERROR: {result_msg}")
                    if not test_mode:
                        self.sheets_manager.update_lead_status(lead['row_number'], "Error")
                    error_count += 1
                
                # Add a small delay between messages to avoid rate limiting
                import time
                time.sleep(1)
            
            # Summary
            logger.info(f"Campaign completed! Success: {success_count}, Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Campaign failed with error: {e}")
            raise
    
    def test_connections(self):
        """Test all API connections."""
        logger.info("Testing API connections...")
        
        # Test Google Sheets
        try:
            leads = self.sheets_manager.read_leads()
            logger.info(f"SUCCESS: Google Sheets: Connected successfully ({len(leads)} leads found)")
        except Exception as e:
            logger.error(f"ERROR: Google Sheets: Connection failed - {e}")
        
        # Test Gemini API
        try:
            sample_lead = {
                'name': 'Test User',
                'region': 'Test Region',
                'interest': 'Test Interest'
            }
            message = self.message_generator.test_generation(sample_lead)
            if message:
                logger.info("SUCCESS: Gemini API: Connected successfully")
            else:
                logger.error("ERROR: Gemini API: Failed to generate test message")
        except Exception as e:
            logger.error(f"ERROR: Gemini API: Connection failed - {e}")
        
        # Test email and WhatsApp connections
        connection_results = self.sender.test_connection()
        
        if connection_results.get('gmail'):
            logger.info("SUCCESS: Gmail SMTP: Connected successfully")
        else:
            logger.error("ERROR: Gmail SMTP: Connection failed")
        
        if connection_results.get('twilio'):
            logger.info("SUCCESS: Twilio WhatsApp: Connected successfully")
        else:
            logger.error("ERROR: Twilio WhatsApp: Connection failed")
    
    def retry_failed_leads(self, sheet_name: str = "outreach_leads"):
        """Reset failed leads back to 'Pending' status for retry."""
        logger.info("Looking for failed leads to retry...")
        
        try:
            all_leads = self.sheets_manager.read_leads(sheet_name)
            failed_leads = [lead for lead in all_leads if lead['status'].lower() == 'error']
            
            if not failed_leads:
                logger.info("No failed leads found.")
                return
            
            logger.info(f"Found {len(failed_leads)} failed leads. Resetting to 'Pending'...")
            
            for lead in failed_leads:
                self.sheets_manager.update_lead_status(lead['row_number'], "Pending")
                logger.info(f"Reset {lead['name']} to Pending status")
            
            logger.info(f"Successfully reset {len(failed_leads)} leads to 'Pending' status")
            
        except Exception as e:
            logger.error(f"Failed to retry leads: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Outreach Assistant - Automated lead outreach')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual sending)')
    parser.add_argument('--test-connections', action='store_true', help='Test all API connections')
    parser.add_argument('--retry-failed', action='store_true', help='Reset failed leads to pending')
    parser.add_argument('--sheet-name', default='outreach_leads', help='Name of the Google Sheet tab')
    
    args = parser.parse_args()
    
    try:
        assistant = OutreachAssistant()
        
        if args.test_connections:
            assistant.test_connections()
        elif args.retry_failed:
            assistant.retry_failed_leads(args.sheet_name)
        else:
            assistant.run_outreach_campaign(test_mode=args.test, sheet_name=args.sheet_name)
            
    except KeyboardInterrupt:
        logger.info("Campaign interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()