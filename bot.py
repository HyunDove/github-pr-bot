import asyncio
import threading

import discord

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, PORT
from webhook_server import create_app, set_discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"[Discord] 봇 로그인: {client.user}")
    loop = asyncio.get_event_loop()
    set_discord(client, loop, DISCORD_CHANNEL_ID)

    app = create_app()
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=PORT, use_reloader=False),
        daemon=True,
    )
    flask_thread.start()
    print(f"[Webhook] 서버 시작: http://0.0.0.0:{PORT}/webhook")
    print("[Bot] PR 감지 대기 중...")


client.run(DISCORD_BOT_TOKEN)
