import json
import os

class NotificationRepository:
    """
    Handles saving and loading notifications to/from a JSON file.
    Acting as our simple local database.
    """
    
    def __init__(self, filepath="notifications.json"):
        # We save the file in the root directory so the frontend can find it easily
        self.filepath = filepath

    def save_all(self, data):
        """
        Saves the entire list of notifications to the file.
        Overwrites the previous file.
        """
        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            return False

    def load_all(self):
        """
        Reads the list of notifications from the file.
        """
        if not os.path.exists(self.filepath):
            return []
            
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return []