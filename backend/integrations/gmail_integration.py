import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GmailIntegration:
    """
    Connects to Gmail API to fetch unread emails.
    Requires: credentials.json (downloaded from Google Cloud Console)
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self):
        self.creds = None
        self.service = None
        
        # We look for token.json (saved login) or credentials.json (new login)
        # Note: We look in the root directory for these files
        self.token_path = 'token.json'
        self.creds_path = 'credentials.json'
        
        self._authenticate()

    def _authenticate(self):
        """Standard Google Authentication Flow"""
        try:
            # 1. Check if we are already logged in
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
            # 2. If not, or if expired, log in again
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if os.path.exists(self.creds_path):
                        flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, self.SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save the login for next time
                        with open(self.token_path, 'w') as token:
                            token.write(self.creds.to_json())
                    else:
                        print("⚠️ Gmail: 'credentials.json' not found. Skipping.")
                        return

            self.service = build('gmail', 'v1', credentials=self.creds)
            
        except Exception as e:
            print(f"❌ Gmail Auth Error: {e}")

    def fetch_emails(self, limit=5):
        """
        Fetches the latest unread emails.
        """
        if not self.service:
            return []

        try:
            # Get list of messages (IDs only)
            results = self.service.users().messages().list(
                userId='me', 
                labelIds=['INBOX', 'UNREAD'], 
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            email_data = []

            # Fetch full details for each message
            for msg in messages:
                txt = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ).execute()
                
                # Extract headers
                headers = txt['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                
                email_data.append({
                    "id": msg['id'],
                    "subject": subject,
                    "from": sender,
                    "snippet": txt.get('snippet', '')
                })
                
            return email_data

        except Exception as e:
            print(f"❌ Gmail Fetch Error: {e}")
            return []