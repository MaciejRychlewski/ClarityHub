import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- PROJECT PATHS ---
# This gets the base directory of your project automatically
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "notifications.json")

# --- APP SETTINGS ---
# If True, we use fake data. If False, we try to connect to real APIs.
DEMO_MODE = True 

# --- PRIORITY THRESHOLDS ---
# The engine calculates a score (0-100). These numbers decide the label.
PRIORITY_THRESHOLDS = {
    "urgent": 85,
    "high": 60,
    "normal": 30,
    # Anything below 30 is "low"
}

# --- SCORING WEIGHTS ---
# How many points is each factor worth?
SCORING_WEIGHTS = {
    "keyword_match": 20,    # Points per keyword (e.g., "ASAP")
    "is_direct_message": 30, # Points if it's a DM (Slack/Discord)
    "is_mention": 25,       # Points if you are @mentioned
    "vip_sender": 25,       # Points if it's from your boss
    "recency_bonus": 10     # Max points for being new
}

# --- KEYWORDS ---
# Words that trigger higher priority
URGENT_KEYWORDS = ["urgent", "asap", "deadline", "immediate", "error", "fail", "alert", "bug"]

# --- VIP SENDERS ---
# Emails or Usernames that are always important (Simulated for Demo)
VIP_SENDERS = ["sarah.chen@company.com", "boss@company.com", "ceo@company.com"]

print("✅ Configuration loaded.")