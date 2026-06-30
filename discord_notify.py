import requests


def build_message(pr: dict, review: dict, issue_urls: list) -> str:
    is_approved = review["status"] == "approved"
    status_emoji = "✅" if is_approved else "❌"
    status_text = "승인" if is_approved else "반려"
    pr_number = pr["number"]
    pr_title = pr["title"]
    pr_author = pr["user"]["login"]
    pr_url = pr["html_url"]

    lines = [
        f"{status_emoji} **PR #{pr_number} {status_text}**",
        f"**제목:** {pr_title}",
        f"**작성자:** {pr_author}",
        "",
        "**요약**",
        review["summary"],
    ]

    severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    issues = review.get("issues", [])
    if issues:
        lines += ["", "**발견된 이슈**"]
        for issue in issues:
            emoji = severity_emoji.get(issue["severity"], "⚪")
            issue_title = issue["title"]
            lines.append(f"{emoji} {issue_title}")

    if issue_urls:
        lines += ["", "**등록된 GitHub 이슈**"]
        for url in issue_urls:
            lines.append(f"• {url}")

    lines += ["", f"🔗 {pr_url}"]

    message = "\n".join(lines)
    if len(message) > 1990:
        message = message[:1990] + "..."
    return message


def send_message(token: str, channel_id: str, message: str):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    resp = requests.post(url, json={"content": message}, headers=headers, timeout=10)
    resp.raise_for_status()