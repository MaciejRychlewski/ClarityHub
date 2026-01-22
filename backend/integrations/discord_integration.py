import os
import requests

class DiscordIntegration:
    """
    Connects to Discord API to fetch messages from a specific channel.
    Requires: DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID in .env
    """
    
    def __init__(self):
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = os.getenv("DISCORD_CHANNEL_ID")
        self.base_url = "https://discord.com/api/v10"

        if not self.token:
            print("⚠️ DISCORD_BOT_TOKEN not found in .env")

    def fetch_messages(self, limit=10):
        """
        Fetches recent messages from the configured channel via REST API.
        """
        if not self.token or not self.channel_id:
            return []

        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }

        try:
            # REST API call to get channel messages
            url = f"{self.base_url}/channels/{self.channel_id}/messages?limit={limit}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Discord Error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Discord Connection Error: {e}")
            return []