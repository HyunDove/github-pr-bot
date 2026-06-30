import json
import sys
import time
from pathlib import Path

# Windows 콘솔 UTF-8 출력
sys.stdout.reconfigure(encoding="utf-8")

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, GITHUB_REPO, POLL_INTERVAL
from discord_notify import build_message, send_message
from github_ops import create_issue, get_open_prs, get_pr_diff, merge_pr, post_pr_comment
from review_pr import review_pr

REVIEWED_FILE = Path(__file__).parent / "reviewed_prs.json"


def load_reviewed() -> set:
    if REVIEWED_FILE.exists():
        return set(json.loads(REVIEWED_FILE.read_text(encoding="utf-8")))
    return set()


def save_reviewed(reviewed: set):
    REVIEWED_FILE.write_text(json.dumps(list(reviewed)), encoding="utf-8")


def handle_pr(pr: dict, reviewed: set):
    pr_number = pr["number"]
    pr_url = pr["url"]

    try:
        print(f"[Bot] PR #{pr_number} 리뷰 시작: {pr['title']}")

        diff = get_pr_diff(GITHUB_REPO, pr_number)
        review = review_pr(
            title=pr["title"],
            author=pr["author"]["login"],
            body=pr.get("body", ""),
            diff=diff,
        )

        post_pr_comment(GITHUB_REPO, pr_number, review["review_comment"])
        print(f"[Bot] PR #{pr_number} 코멘트 등록 완료")

        issue_urls = []
        for issue in review.get("issues", []):
            if issue.get("create_github_issue"):
                problem  = issue.get("problem", "")
                cause    = issue.get("cause", "")
                solution = issue.get("solution", "")
                body = (
                    f"## 문제\n{problem}\n\n"
                    f"## 원인\n{cause}\n\n"
                    f"## 해결 방법\n{solution}\n\n"
                    f"---\nPR #{pr_number}: {pr_url}"
                )
                url = create_issue(
                    repo=GITHUB_REPO,
                    title=f"[PR #{pr_number}] {issue['title']}",
                    body=body,
                )
                issue_urls.append(url)
                print(f"[Bot] 이슈 등록: {url}")

        if review.get("status") == "approved":
            try:
                merge_pr(GITHUB_REPO, pr_number)
                print(f"[Bot] PR #{pr_number} 자동 머지 완료")
            except Exception as e:
                print(f"[ERROR] 머지 실패: {e}")

        pr_for_message = {
            "number": pr["number"],
            "title": pr["title"],
            "user": {"login": pr["author"]["login"]},
            "html_url": pr["url"],
        }
        message = build_message(pr_for_message, review, issue_urls)

        if DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID:
            send_message(DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, message)
            print(f"[Discord] PR #{pr_number} 알림 전송 완료")

        reviewed.add(pr_number)
        save_reviewed(reviewed)

    except Exception as e:
        print(f"[ERROR] PR #{pr_number} 처리 실패: {e}")
        import traceback; traceback.print_exc()


def main():
    if not GITHUB_REPO:
        print("[ERROR] .env에 GITHUB_REPO가 설정되지 않았습니다.")
        return

    print(f"[Bot] 폴링 시작 - {GITHUB_REPO} ({POLL_INTERVAL}초 간격)")
    reviewed = load_reviewed()
    print(f"[Bot] 이미 리뷰된 PR: {reviewed}")

    while True:
        try:
            prs = get_open_prs(GITHUB_REPO)
            new_prs = [pr for pr in prs if pr["number"] not in reviewed]
            if new_prs:
                for pr in new_prs:
                    handle_pr(pr, reviewed)
            else:
                print(f"[Bot] 새 PR 없음 (열린 PR: {len(prs)}개)")
        except Exception as e:
            print(f"[ERROR] 폴링 실패: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()