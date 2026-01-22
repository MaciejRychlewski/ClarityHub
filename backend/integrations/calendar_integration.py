import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class CalendarIntegration:
    """
    Connects to Google Calendar to fetch upcoming events.
    Requires: credentials.json
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = 'token.json'
        self.creds_path = 'credentials.json'
        
        self._authenticate()

    def _authenticate(self):
        """Same Auth flow as Gmail"""
        try:
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if os.path.exists(self.creds_path):
                        flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, self.SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        with open(self.token_path, 'w') as token:
                            token.write(self.creds.to_json())
                    else:
                        # Fail silently so we don't spam errors if user didn't set it up
                        return

            self.service = build('calendar', 'v3', credentials=self.creds)
            
        except Exception as e:
            print(f"❌ Calendar Auth Error: {e}")

    def fetch_events(self, max_results=5):
        """
        Fetches the next upcoming events.
        """
        if not self.service:
            return []

        try:
            now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            clean_events = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                clean_events.append({
                    "title": event.get('summary', 'Busy'),
                    "start": start,
                    "link": event.get('htmlLink', '#'),
                    "creator": event.get('creator', {}).get('email', 'Calendar')
                })
                
            return clean_events

        except Exception as e:
            print(f"❌ Calendar Fetch Error: {e}")
            return []