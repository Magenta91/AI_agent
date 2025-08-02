#!/usr/bin/env python3
"""
Quick script to check available sheets in the Google Sheets document
"""

import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

def check_sheets():
    try:
        # Authenticate
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        print("Available sheets:")
        for sheet in spreadsheet['sheets']:
            sheet_name = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            print(f"  - {sheet_name} (ID: {sheet_id})")
        
        # Try to read from the first sheet
        first_sheet = spreadsheet['sheets'][0]['properties']['title']
        print(f"\nTrying to read from '{first_sheet}':")
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{first_sheet}!A1:Z10"  # Read first 10 rows, all columns
        ).execute()
        
        values = result.get('values', [])
        if values:
            print("Sample data:")
            for i, row in enumerate(values[:5]):  # Show first 5 rows
                print(f"  Row {i+1}: {row}")
        else:
            print("No data found in the sheet")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sheets()