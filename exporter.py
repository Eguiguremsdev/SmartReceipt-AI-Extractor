import os
import csv
import logging
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config

logger = logging.getLogger(__name__)

class Exporter:
    """Handles exporting data to CSV and Google Sheets."""

    def __init__(self):
        self.csv_path = Config.DATA_LOG
        self.error_log_path = Config.ERROR_LOG
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        """Creates the CSV file with headers if it doesn't exist."""
        headers = ['Timestamp', 'Filename', 'Date', 'Vendor Name', 'Category', 'Subtotal', 'Tax', 'Total', 'Currency', 'Validation Passed']
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info(f"Created new CSV file: {self.csv_path}")

    def log_error(self, filename: str, error_message: str):
        """Logs skipped files or errors into the error log."""
        timestamp = datetime.datetime.now().isoformat()
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] File: {filename} - Error: {error_message}\n")
        logger.error(f"Logged error for {filename}")

    def save_to_csv(self, filename: str, data: dict):
        """Appends extracted data to the local CSV file."""
        timestamp = datetime.datetime.now().isoformat()
        
        row = [
            timestamp,
            filename,
            data.get('date', ''),
            data.get('vendor_name', ''),
            data.get('category', ''),
            data.get('subtotal', 0.0),
            data.get('tax', 0.0),
            data.get('total', 0.0),
            data.get('currency', ''),
            data.get('validation_passed', False)
        ]

        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            logger.info(f"Saved data to CSV for {filename}")
        except Exception as e:
            logger.error(f"Failed to save to CSV: {e}")
            self.log_error(filename, f"CSV Save Error: {e}")

    def push_to_google_sheets(self, filename: str, data: dict):
        """Pushes the extracted data to Google Sheets."""
        if not Config.GOOGLE_SPREADSHEET_ID:
            logger.info("Google Sheets ID not configured. Skipping sheets export.")
            return

        if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            logger.error(f"Google credentials file '{Config.GOOGLE_CREDENTIALS_FILE}' not found. Cannot push to Sheets.")
            self.log_error(filename, "Missing Google Credentials File")
            return

        try:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = service_account.Credentials.from_service_account_file(
                Config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)

            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()

            timestamp = datetime.datetime.now().isoformat()
            
            # Values must be strings/numbers in a list of lists
            values = [[
                timestamp,
                filename,
                data.get('date', ''),
                data.get('vendor_name', ''),
                data.get('category', ''),
                data.get('subtotal', 0.0),
                data.get('tax', 0.0),
                data.get('total', 0.0),
                data.get('currency', ''),
                str(data.get('validation_passed', False))
            ]]

            body = {'values': values}

            range_name = f"{Config.GOOGLE_SHEET_NAME}!A:J"

            result = sheet.values().append(
                spreadsheetId=Config.GOOGLE_SPREADSHEET_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()

            logger.info(f"Successfully pushed data to Google Sheets. Updated {result.get('updates').get('updatedCells')} cells.")

        except Exception as e:
             logger.error(f"Failed to push to Google Sheets: {e}")
             self.log_error(filename, f"Google Sheets API Error: {e}")

    def export_all(self, filename: str, data: dict):
        """Orchestrates both CSV save and Google Sheets push."""
        self.save_to_csv(filename, data)
        self.push_to_google_sheets(filename, data)
