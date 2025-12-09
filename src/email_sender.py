# Make sure these imports are at the top of your file
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Shows basic usage of the Gmail API."""
    creds = None
    
    # 1. DEFINE ABSOLUTE PATHS
    # We get the folder where THIS script (email_sender.py) lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # We go up one level to the project root (where .env and json files should be)
    project_root = os.path.join(current_dir, '..')
    
    # Define the exact paths we want to use
    token_path = os.path.join(project_root, 'token.json')
    creds_path = os.path.join(project_root, 'credentials.json')

    # 2. CLOUD FIX: Create files from Environment Variables if they are missing
    # This runs on Render to "restore" the files from the settings you added
    if not os.path.exists(token_path):
        token_content = os.environ.get("GMAIL_TOKEN_CONTENT")
        if token_content:
            print(f"Creating token.json at {token_path}...")
            with open(token_path, 'w') as f:
                f.write(token_content)
        else:
            print(f"⚠️ Warning: GMAIL_TOKEN_CONTENT not found in env vars. looked at {token_path}")

    if not os.path.exists(creds_path):
        creds_content = os.environ.get("GMAIL_CREDENTIALS_CONTENT")
        if creds_content:
            print(f"Creating credentials.json at {creds_path}...")
            with open(creds_path, 'w') as f:
                f.write(creds_content)
        else:
             print(f"⚠️ Warning: GMAIL_CREDENTIALS_CONTENT not found in env vars. looked at {creds_path}")

    # 3. AUTHENTICATION FLOW
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This part usually only runs on your local machine
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service
