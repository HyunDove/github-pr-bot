def build_message(pr: dict, review: dict, issue_urls: list) -> str:
    is_approved = review["status"] == "approved"
    status_emoji = "✅" if is_approved else "❌"
    status_text = "승인" if is_approved else "반려"

    lines = [
        f"{status_emoji} **PR #{pr['number']} {status_text}**",
        f"**제목:** {pr['title']}",
        f"**작성자:** {pr['user']['login']}",
        "",
        f"**요약**",
        review["summary"],
    ]

    severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    issues = review.get("issues", [])
    if issues:
        lines += ["", "**발견된 이슈**"]
        for issue in issues:
            emoji = severity_emoji.get(issue["severity"], "⚪")
            lines.append(f"{emoji} {issue['title']}")

    if issue_urls:
        lines += ["", "**등록된 GitHub 이슈**"]
        for url in issue_urls:
            lines.append(f"• {url}")

    lines += ["", f"🔗 {pr['html_url']}"]

    message = "\n".join(lines)
    if len(message) > 1990:
        message = message[:1990] + "..."
    return message
