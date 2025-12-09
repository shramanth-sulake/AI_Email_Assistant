import os
import json
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Shows basic usage of the Gmail API."""
    creds = None
    
    # --- 1. DEFINE ABSOLUTE PATHS ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..')
    
    token_path = os.path.join(project_root, 'token.json')
    creds_path = os.path.join(project_root, 'credentials.json')

    # --- 2. CLOUD FIX: Restore files from Env Vars ---
    if not os.path.exists(token_path):
        token_content = os.environ.get("GMAIL_TOKEN_CONTENT")
        if token_content:
            print(f"Creating token.json at {token_path}...")
            with open(token_path, 'w') as f:
                f.write(token_content)
    
    if not os.path.exists(creds_path):
        creds_content = os.environ.get("GMAIL_CREDENTIALS_CONTENT")
        if creds_content:
            print(f"Creating credentials.json at {creds_path}...")
            with open(creds_path, 'w') as f:
                f.write(creds_content)

    # --- 3. AUTHENTICATION ---
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

# ⚠️ IMPORTANT: This function must be all the way to the left (Level 0 Indentation)
def send_email(recipient_email, subject, body):
    """Creates and sends an email message."""
    try:
        service = get_gmail_service()

        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient_email
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        print(f'Message Id: {send_message["id"]}')
        return True, "Email sent successfully!"
        
    except Exception as e:
        print(f'An error occurred: {e}')
        return False, str(e)
