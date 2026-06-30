import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, GITHUB_REPO, POLL_INTERVAL
from discord_notify import build_message, send_message
from github_ops import (
    close_issue, create_issue, get_open_prs, get_pr_diff,
    merge_pr, post_pr_comment,
)
from review_pr import review_pr

STATE_FILE = Path(__file__).parent / "pr_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def handle_pr(pr: dict, state: dict, is_recheck: bool = False):
    pr_number = pr["number"]
    pr_url = pr["url"]
    sha = pr["headRefOid"]

    try:
        label = "재검증" if is_recheck else "신규 리뷰"
        print(f"[Bot] PR #{pr_number} {label} 시작: {pr['title']}")

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
        new_issue_numbers = []

        if review.get("status") == "approved":
            # 재검증 통과: 기존 이슈 close
            if is_recheck:
                old_issue_numbers = state.get(str(pr_number), {}).get("issue_numbers", [])
                for issue_num in old_issue_numbers:
                    try:
                        close_issue(GITHUB_REPO, issue_num)
                        print(f"[Bot] GitHub 이슈 #{issue_num} close 완료")
                    except Exception as e:
                        print(f"[ERROR] 이슈 #{issue_num} close 실패: {e}")

            merge_pr(GITHUB_REPO, pr_number)
            print(f"[Bot] PR #{pr_number} 자동 머지 완료")

        else:
            # 반려: 이슈 등록
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
                    url, issue_number = create_issue(
                        repo=GITHUB_REPO,
                        title=f"[PR #{pr_number}] {issue['title']}",
                        body=body,
                    )
                    issue_urls.append(url)
                    new_issue_numbers.append(issue_number)
                    print(f"[Bot] 이슈 등록: {url}")

        # 상태 저장
        state[str(pr_number)] = {
            "status": review["status"],
            "sha": sha,
            "issue_numbers": new_issue_numbers,
        }
        save_state(state)

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

    except Exception as e:
        print(f"[ERROR] PR #{pr_number} 처리 실패: {e}")
        import traceback; traceback.print_exc()


def main():
    if not GITHUB_REPO:
        print("[ERROR] .env에 GITHUB_REPO가 설정되지 않았습니다.")
        return

    print(f"[Bot] 폴링 시작 - {GITHUB_REPO} ({POLL_INTERVAL}초 간격)")
    state = load_state()
    print(f"[Bot] 추적 중인 PR: {list(state.keys())}")

    while True:
        try:
            prs = get_open_prs(GITHUB_REPO)
            for pr in prs:
                pr_key = str(pr["number"])
                saved = state.get(pr_key)

                if saved is None:
                    # 신규 PR
                    handle_pr(pr, state, is_recheck=False)

                elif saved["status"] == "rejected" and saved["sha"] != pr["headRefOid"]:
                    # 반려된 PR에 새 커밋 감지 → 재검증
                    print(f"[Bot] PR #{pr['number']} 새 커밋 감지 - 재검증 시작")
                    handle_pr(pr, state, is_recheck=True)

            if not any(
                state.get(str(pr["number"])) is None or
                (state.get(str(pr["number"]), {}).get("status") == "rejected" and
                 state.get(str(pr["number"]), {}).get("sha") != pr["headRefOid"])
                for pr in prs
            ):
                print(f"[Bot] 처리할 PR 없음 (열린 PR: {len(prs)}개)")

        except Exception as e:
            print(f"[ERROR] 폴링 실패: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()