import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))