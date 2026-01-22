# Clarity Hub | Intelligent Notification Aggregator

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Backend-Python_3.9+-blue)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla_JS_%7C_Tailwind-purple)

**Clarity Hub** is a centralized dashboard designed to combat notification fatigue. It aggregates streams from Slack, GitHub, Jira, and Calendars into a single view, using a **custom Priority Engine** to algorithmically sort noise from signal.

## 🚀 Key Features

* **Unified Ingestion:** Connects to multiple API sources (Slack, Jira, GitHub, Gmail) to pull disparate data streams.
* **Algorithmic Prioritization:** A custom Python engine scores every notification (0-100) based on keywords, sender reputation, and NLP heuristics to classify them as *Urgent*, *High*, or *Normal*.
* **Glassmorphism UI:** A responsive, modern dashboard built with Tailwind CSS and Vanilla JS (No heavy frameworks).
* **Dual-Mode Engine:** Runs in `Live Mode` (Real APIs) or `Demo Mode` (Synthetic Data Generator for testing/showcasing).

## 🛠️ Architecture

The system follows a standard ETL (Extract, Transform, Load) pattern:

1.  **Extract:** `Aggregator` fetches raw JSON data from configured APIs.
2.  **Transform:** `PriorityEngine` analyzes text content and assigns a weighted score.
3.  **Load:** Processed data is stored in a local JSON repository.
4.  **Visualize:** Frontend polls the repository to render the Bento Grid dashboard.

## 📂 Project Structure

```text
backend/
├── integrations/       # API Clients (Slack, GitHub, Jira)
├── processing/         # Priority Logic & Scoring Engine
├── storage/            # JSON Persistence Layer
└── run_aggregator.py   # Main Pipeline Orchestrator

frontend/
├── index.html          # Dashboard UI
└── main.js             # Logic for Modals, Time-parsing, and Rendering

1. Installation
# Clone repository
git clone [https://github.com/MaciejRychlewski/clarity-hub.git]
cd clarity-hub

# Install dependencies (if you have a requirements file)
# pip install -r requirements.txt

2. Configuration
# Create a .env file the root directory

# Toggle between Real/Fake data
DEMO_MODE=True 

# Optional: Real API Keys
SLACK_BOT_TOKEN=xoxb-...
GITHUB_TOKEN=ghp-...

3. Run the pipeline
# Step 1: Generate/Fetch data (Backend)
python3 -m backend.run_aggregator

# Step 2: Launch the Dashboard (Frontend)
python3 -m http.server 8000

# Step 3: Visit http://localhost:8000/frontend/ to view the dashboard.

Built by Maciej Rychlewski as a Portfolio Project.