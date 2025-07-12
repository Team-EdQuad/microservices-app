from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "edquad-23435052a937.json")
FOLDER_IDS = {
    "content": "1OFRASPSsndJEDCLaywsDiXo-Jbb9_YWt",
    "assignments": "1IwE3pQF9TgGPf-0vg7WrPShgEkCcshcr", 
    "submissions": "1Yb31vqo2VlwXavh8SWTZuOBLSQu5_vIC"}

def get_drive_service():
    """Initialize and return Google Drive API service."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)