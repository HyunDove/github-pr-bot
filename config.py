import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))