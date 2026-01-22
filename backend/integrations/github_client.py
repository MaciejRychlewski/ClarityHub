import os
import requests
from datetime import datetime

class GitHubClient:
    """
    Real integration with GitHub API.
    Fetches Pull Requests where the user is requested for review or assigned.
    """
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_data(self):
        """
        Main entry point used by the aggregator.
        Returns a list of standardized notification dictionaries.
        """
        if not self.token:
            print("⚠️ GitHub Token missing. Skipping.")
            return []

        notifications = []
        
        # 1. Get PRs where I am requested for review
        notifications.extend(self._get_review_requests())
        
        # 2. Get Issues/PRs assigned to me
        notifications.extend(self._get_assignments())
        
        return notifications

    def _get_review_requests(self):
        # Query: type:pr state:open review-requested:@me
        params = {'q': 'type:pr state:open review-requested:@me'}
        return self._execute_search(params, "Review Required", "high")

    def _get_assignments(self):
        # Query: assignee:@me state:open
        params = {'q': 'assignee:@me state:open'}
        return self._execute_search(params, "Assigned to You", "normal")

    def _execute_search(self, params, prefix, default_priority):
        results = []
        try:
            response = requests.get(f"{self.base_url}/search/issues", headers=self.headers, params=params)
            if response.status_code == 200:
                items = response.json().get('items', [])
                for item in items:
                    results.append({
                        "id": str(item['id']),
                        "source": "github",
                        "type": "pr",
                        "title": f"{prefix}: {item['title']}",
                        "content": f"Repo: {item['repository_url'].split('/')[-1]}",
                        "sender": {"name": item['user']['login'], "email": ""},
                        "timestamp": item['created_at'], # ISO format
                        "priority": default_priority,
                        "url": item['html_url']
                    })
            else:
                print(f"❌ GitHub Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error connecting to GitHub: {e}")
        
        return results