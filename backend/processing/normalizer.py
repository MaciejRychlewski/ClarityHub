import uuid
from datetime import datetime

class NotificationNormalizer:
    """
    Standardizes data from different sources (Slack, Gmail, etc.) 
    into a unified format for the Dashboard.
    """

    def normalize(self, raw_data, source_type):
        """
        Input: Raw dictionary from API
        Output: Clean dictionary matching our Data Model
        """
        # 1. Create a skeleton with defaults
        norm = {
            "id": str(uuid.uuid4()),
            "source": source_type,
            "type": "message",
            "title": "New Notification",
            "content": "",
            "sender": {"name": "Unknown", "email": ""},
            "timestamp": datetime.now().isoformat(),
            "priority": "normal", # Will be updated by Engine later
            "is_read": False,
            "channel": "General",
            "url": "#",
            "tags": [],
            "priority_score": 0
        }

        # 2. Map fields based on source
        if source_type == "slack":
            # Real Slack API returns 'text' and 'user' ID
            norm["content"] = raw_data.get("text", "")
            norm["channel"] = raw_data.get("channel_name", "#general")
            # In a real app, we would look up the user ID to get a name
            norm["sender"]["name"] = raw_data.get("user", "Slack User")
            norm["url"] = raw_data.get("permalink", "#")
            
        elif source_type == "gmail":
            # Real Gmail API returns headers (Subject, From) and snippet
            norm["title"] = raw_data.get("subject", "No Subject")
            norm["content"] = raw_data.get("snippet", "")
            norm["sender"]["name"] = raw_data.get("from", "Email Sender")
            norm["type"] = "email"
            
        elif source_type == "discord":
            norm["content"] = raw_data.get("content", "")
            norm["sender"]["name"] = raw_data.get("author", "Discord User")
            norm["channel"] = raw_data.get("channel", "Discord")

        # 3. If it's already in our Mock format (internal), just pass it through
        if "title" in raw_data and "content" in raw_data:
            norm.update(raw_data)

        return norm