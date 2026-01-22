import random
import uuid
from datetime import datetime, timedelta

class MockGenerator:
    """
    Generates data with specific KEYWORDS to trigger the Priority Engine.
    """
    def generate(self, count=60):
        data = []
        
        # === 1. FORCE URGENT ITEMS (Red Box) ===
        # We create 6 specific items guaranteed to be 'urgent'
        for _ in range(6):
            data.append(self._create_item("slack", "urgent", "CRITICAL: Production DB Down", "Database connection failed. Immediate action required."))
            data.append(self._create_item("jira", "urgent", "URGENT: Checkout 500 Error", "Users cannot pay. Sev-1 Incident."))
            
        # === 2. FORCE IMPORTANT ITEMS (Blue Box) ===
        # We create 6 specific items guaranteed to be 'high'
        for _ in range(6):
            data.append(self._create_item("gmail", "high", "Security Alert: New Login", "New login detected from unknown IP."))
            data.append(self._create_item("github", "high", "Review Required: Auth API", "PR #1024 needs review before deployment."))

        # === 3. CALENDAR ===
        for _ in range(4): data.append(self._create_calendar_event())

        # === 4. FILLER STREAM (The rest) ===
        sources = ['discord', 'slack', 'gmail', 'github', 'jira']
        # Calculate remaining slots to fill
        remaining = count - len(data)
        
        for _ in range(max(0, remaining)):
            source = random.choice(sources)
            data.append(self._create_item(source, "normal", "Generic Update", "Just a normal message to fill the stream."))

        data.sort(key=lambda x: x['timestamp'], reverse=True)
        return data

    def _create_item(self, source, priority, title, content):
        # Maps sources to nice sender names
        senders = {
            "slack": "DevOps Bot", "gmail": "AWS Billing", 
            "discord": "Community Mgr", "github": "Dependabot", 
            "jira": "Jira System"
        }
        
        return {
            "id": str(uuid.uuid4()),
            "source": source,
            "type": "message",
            "title": title,
            "content": content,
            "sender": {"name": senders.get(source, "System"), "email": ""},
            "timestamp": self._random_past_time(),
            "priority": priority, 
            # Force high score if priority is high/urgent so the backend doesn't downgrade it
            "priority_score": 95 if priority == "urgent" else (80 if priority == "high" else 20)
        }

    def _random_past_time(self):
        minutes_back = random.randint(1, 2800)
        past_time = datetime.now() - timedelta(minutes=minutes_back)
        return past_time.isoformat()

    def _create_calendar_event(self):
        titles = ["Team Standup", "Client Call", "Deep Work", "Project Review"]
        future_time = (datetime.now() + timedelta(hours=random.randint(1, 100))).isoformat()
        return {
            "id": str(uuid.uuid4()), "source": "calendar", "type": "event",
            "title": random.choice(titles), "content": "Zoom Link",
            "sender": {"name": "Google Calendar", "email": ""},
            "timestamp": future_time, "priority": "normal", "priority_score": 50
        }