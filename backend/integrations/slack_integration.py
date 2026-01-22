import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackIntegration:
    """
    Connects to Slack API to fetch recent messages.
    Requires: SLACK_BOT_TOKEN in .env
    """
    
    def __init__(self):
        # We look for the token in environment variables
        self.token = os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            print("⚠️ SLACK_BOT_TOKEN not found in .env")
            self.client = None
        else:
            self.client = WebClient(token=self.token)

    def fetch_messages(self, channel_id=None, limit=10):
        """
        Fetches last 'limit' messages from a channel.
        """
        if not self.client:
            return []

        # If no channel provided, try to use a default or find general
        if not channel_id:
            channel_id = os.getenv("SLACK_CHANNEL_ID")

        if not channel_id:
            print("⚠️ SLACK_CHANNEL_ID not set. Cannot fetch.")
            return []

        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            
            messages = []
            for msg in response["messages"]:
                # We add 'channel_name' manually so the normalizer can see it
                # (In a full app, we'd fetch info for the channel ID)
                msg['channel_name'] = "Slack Channel"
                messages.append(msg)
                
            return messages

        except SlackApiError as e:
            print(f"❌ Slack API Error: {e.response['error']}")
            return []