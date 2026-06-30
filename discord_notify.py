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
        f"📌 **제목:** {pr_title}",
        f"👤 **작성자:** {pr_author}",
        "",
        "📋 **리뷰 요약**",
        review["summary"],
    ]

    severity_map = {
        "critical": ("🔴", "치명적"),
        "warning":  ("🟡", "경고"),
        "info":     ("🔵", "정보"),
    }

    issues = review.get("issues", [])
    if issues:
        lines += ["", f"⚠️ **발견된 이슈 ({len(issues)}건)**", "━━━━━━━━━━━━━━━━━━━"]
        for issue in issues:
            emoji, label = severity_map.get(issue["severity"], ("⚪", "기타"))
            issue_title = issue["title"]
            lines.append(f"{emoji} **[{label}] {issue_title}**")
            if issue.get("problem"):
                lines.append(f"❓ **문제:** {issue['problem']}")
            if issue.get("cause"):
                lines.append(f"💡 **원인:** {issue['cause']}")
            if issue.get("solution"):
                lines.append(f"🔧 **해결:** {issue['solution']}")
            lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━")

    if issue_urls:
        lines += ["", "📌 **등록된 GitHub 이슈**"]
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