import threading

from flask import Flask

from config import DISCORD_BOT_TOKEN, PORT
from webhook_server import create_app


def main():
    app = create_app()
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=PORT, use_reloader=False),
        daemon=True,
    )
    flask_thread.start()
    print(f"[Webhook] 서버 시작: http://0.0.0.0:{PORT}/webhook")
    print("[Bot] PR 감지 대기 중...")
    flask_thread.join()


if __name__ == "__main__":
    main()