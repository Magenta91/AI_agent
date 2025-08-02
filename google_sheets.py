import os
import logging
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account credentials."""
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Successfully authenticated with Google Sheets API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def read_leads(self, sheet_name: str = "outreach_leads", range_name: str = "A:E") -> List[Dict]:
        """Read leads from Google Sheets and return as list of dictionaries."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("No data found in the sheet")
                return []
            
            # Assume first row contains headers
            headers = values[0]
            leads = []
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2
                # Pad row with empty strings if it's shorter than headers
                while len(row) < len(headers):
                    row.append("")
                
                lead = {
                    'row_number': i,
                    'name': row[0] if len(row) > 0 else "",
                    'contact': row[1] if len(row) > 1 else "",
                    'interest': row[2] if len(row) > 2 else "",
                    'region': row[3] if len(row) > 3 else "",
                    'status': row[4] if len(row) > 4 else "Pending"
                }
                leads.append(lead)
            
            logger.info(f"Successfully read {len(leads)} leads from sheet")
            return leads
            
        except HttpError as e:
            logger.error(f"HTTP error reading from Google Sheets: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading from Google Sheets: {e}")
            raise
    
    def update_lead_status(self, row_number: int, status: str, sheet_name: str = "outreach_leads"):
        """Update the status of a specific lead in the Google Sheet."""
        try:
            # Column E (index 4) is the status column
            range_name = f"{sheet_name}!E{row_number}"
            
            body = {
                'values': [[status]]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated row {row_number} status to '{status}'")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error updating Google Sheets: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating Google Sheets: {e}")
            raise
    
    def get_pending_leads(self, sheet_name: str = "outreach_leads") -> List[Dict]:
        """Get only leads with 'Pending' status."""
        all_leads = self.read_leads(sheet_name)
        pending_leads = [lead for lead in all_leads if lead['status'].lower() == 'pending']
        logger.info(f"Found {len(pending_leads)} pending leads")
        return pending_leads