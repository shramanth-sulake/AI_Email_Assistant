import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    # We look for token.json in the parent directory (project root)
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(recipient_email, subject, body):
    """Creates and sends an email message."""
    try:
        service = get_gmail_service()

        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient_email
        message['Subject'] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        print(f'Message Id: {send_message["id"]}')
        return True, "Email sent successfully!"
        
    except Exception as e:
        print(f'An error occurred: {e}')
        return False, str(e)

# --- TEST BLOCK (Runs only if you run this file directly) ---
if __name__ == '__main__':
    print("Attempting to authenticate...")
    # Replace with your own email to test!
    recipient = input("Enter an email address to send a test to: ")
    success, msg = send_email(recipient, "Test from Ghostwriter", "Hello! If you see this, the Gmail API is working.")
    print(msg)