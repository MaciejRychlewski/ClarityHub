import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

class JiraClient:
    """
    Real integration with Atlassian Jira API.
    Fetches unresolved tickets assigned to the user.
    """
    
    def __init__(self):
        self.domain = os.getenv("JIRA_DOMAIN")  # e.g., "yourcompany" (for yourcompany.atlassian.net)
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.base_url = f"https://{self.domain}.atlassian.net/rest/api/3" if self.domain else None

    def fetch_data(self):
        """
        Main entry point. Returns standardized notifications.
        """
        if not self.token or not self.domain or not self.email:
            print("⚠️ Jira credentials missing. Skipping.")
            return []

        notifications = []
        
        # JQL: assigned to me AND not done order by priority
        jql = "assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC"
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers={"Accept": "application/json"},
                params={'jql': jql, 'maxResults': 10},
                auth=HTTPBasicAuth(self.email, self.token)
            )
            
            if response.status_code == 200:
                issues = response.json().get('issues', [])
                for issue in issues:
                    fields = issue['fields']
                    priority_name = fields['priority']['name'].lower()
                    
                    # Map Jira priority to our system
                    our_priority = "normal"
                    if priority_name in ['highest', 'high', 'critical']:
                        our_priority = "urgent"
                    elif priority_name in ['medium']:
                        our_priority = "high"

                    notifications.append({
                        "id": issue['id'],
                        "source": "jira",
                        "type": "ticket",
                        "title": f"{issue['key']}: {fields['summary']}",
                        "content": f"Status: {fields['status']['name']}",
                        "sender": {"name": "Jira", "email": ""},
                        "timestamp": fields['created'], # usually ISO format
                        "priority": our_priority,
                        "url": f"https://{self.domain}.atlassian.net/browse/{issue['key']}"
                    })
            else:
                print(f"❌ Jira Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error connecting to Jira: {e}")
            
        return notifications