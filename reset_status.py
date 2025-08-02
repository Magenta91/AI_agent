#!/usr/bin/env python3
"""
Reset a specific lead's status back to Pending for testing
"""

import os
from dotenv import load_dotenv
from google_sheets import GoogleSheetsManager

load_dotenv()

def reset_lead_status():
    try:
        sheets_manager = GoogleSheetsManager(
            credentials_path=os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID')
        )
        
        # Reset Abhishek (row 3) back to Pending
        sheets_manager.update_lead_status(3, "Pending")
        print("Successfully reset Abhishek's status to 'Pending'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_lead_status()