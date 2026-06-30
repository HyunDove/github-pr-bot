import hashlib
import hmac
import threading

from flask import Flask, abort, request

from config import GITHUB_WEBHOOK_SECRET, PORT
from discord_notify import build_message
from github_ops import create_issue, get_pr_diff, post_pr_comment
from review_pr import review_pr

_discord_client = None
_event_loop = None
_channel_id = None


def set_discord(client, loop, channel_id):
    global _discord_client, _event_loop, _channel_id
    _discord_client = client
    _event_loop = loop
    _channel_id = channel_id


def _verify_signature(payload: bytes, signature: str) -> bool:
    if not GITHUB_WEBHOOK_SECRET:
        return True
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def _handle_pr(payload: dict):
    import asyncio

    pr = payload["pull_request"]
    repo = payload["repository"]["full_name"]
    pr_number = pr["number"]

    try:
        diff = get_pr_diff(repo, pr_number)
        review = review_pr(
            title=pr["title"],
            author=pr["user"]["login"],
            body=pr.get("body", ""),
            diff=diff,
        )

        post_pr_comment(repo, pr_number, review["review_comment"])

        issue_urls = []
        for issue in review.get("issues", []):
            if issue.get("create_github_issue"):
                url = create_issue(
                    repo=repo,
                    title=f"[PR #{pr_number}] {issue['title']}",
                    body=f"PR #{pr_number} 리뷰 중 발견\n\n{issue['description']}\n\n{pr['html_url']}",
                )
                issue_urls.append(url)

        message = build_message(pr, review, issue_urls)

        if _discord_client and _event_loop and _channel_id:
            async def _send():
                channel = _discord_client.get_channel(_channel_id)
                if channel:
                    await channel.send(message)

            asyncio.run_coroutine_threadsafe(_send(), _event_loop)

    except Exception as e:
        print(f"[ERROR] PR 처리 실패: {e}")


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not _verify_signature(request.data, signature):
            abort(401)

        payload = request.get_json(silent=True)
        event = request.headers.get("X-GitHub-Event", "")

        if event == "pull_request" and payload and payload.get("action") in ("opened", "synchronize"):
            threading.Thread(target=_handle_pr, args=(payload,), daemon=True).start()

        return "OK", 200

    return app
