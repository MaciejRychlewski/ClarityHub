import logging
import os
from dotenv import load_dotenv

# Integrations
from backend.integrations.slack_integration import SlackIntegration
from backend.integrations.github_client import GitHubClient
from backend.integrations.jira_client import JiraClient
from backend.integrations.mock_generator import MockGenerator

# Core Systems
from backend.processing.priority_engine import PriorityEngine
from backend.storage.repository import NotificationRepository

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

class NotificationAggregator:
    """
    Orchestrator for the Clarity Hub pipeline.
    Fetches data from configured sources, runs priority analysis, and persists to storage.
    """
    
    def __init__(self):
        load_dotenv()
        self.demo_mode = os.getenv("DEMO_MODE", "True").lower() == "true"
        self.repository = NotificationRepository()
        self.priority_engine = PriorityEngine()

    def run(self):
        logging.info("🚀 Pipeline Started")
        raw_data = []

        # --- Ingestion Phase ---
        if self.demo_mode:
            logging.info("⚠️  Demo Mode: Generating synthetic data stream")
            generator = MockGenerator()
            raw_data = generator.generate(count=60)
        else:
            logging.info("🔌 Live Mode: Connecting to external APIs")
            raw_data.extend(self._fetch_slack())
            raw_data.extend(self._fetch_github())
            raw_data.extend(self._fetch_jira())

        logging.info(f"📥 Ingested {len(raw_data)} items")

        # --- Processing Phase ---
        prioritized_data = self.priority_engine.process(raw_data)
        
        # --- Storage Phase ---
        self.repository.save_all(prioritized_data)
        
        urgent_count = sum(1 for n in prioritized_data if n['priority'] == 'urgent')
        logging.info(f"✅ Pipeline Complete. Persisted {len(prioritized_data)} items ({urgent_count} Urgent).")

    # --- Helper Methods for Error Isolation ---
    def _fetch_slack(self):
        try:
            return SlackIntegration().fetch_messages(limit=10)
        except Exception as e:
            logging.error(f"Slack Integration Failed: {e}")
            return []

    def _fetch_github(self):
        try:
            return GitHubClient().fetch_data()
        except Exception as e:
            logging.error(f"GitHub Integration Failed: {e}")
            return []

    def _fetch_jira(self):
        try:
            return JiraClient().fetch_data()
        except Exception as e:
            logging.error(f"Jira Integration Failed: {e}")
            return []

if __name__ == "__main__":
    NotificationAggregator().run()