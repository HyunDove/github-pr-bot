# GitHub PR Review Bot

Claude Code CLI가 PR을 자동 리뷰하고, 결과를 Discord로 알리며, critical 이슈 발견 시 GitHub 이슈를 자동 등록하는 로컬 봇입니다.

- **Claude API 키 불필요** — 로컬 Claude Code CLI 사용
- **터널 불필요** — GitHub API 폴링 방식
- **자동 재검증** — 코드 수정 후 새 커밋 push 시 재리뷰 및 이슈 자동 close

---

## 동작 흐름

```
bot.py (30초 폴링)
  └─ 새 PR 감지
       ├─ Claude Code로 코드 리뷰
       ├─ PR 코멘트 게시
       ├─ critical → GitHub 이슈 자동 등록
       ├─ 승인 → PR 자동 머지
       └─ Discord 알림

새 커밋 push (SHA 변경 감지)
  └─ 자동 재검증
       ├─ 통과 → GitHub 이슈 close + 머지
       └─ 실패 → 새 이슈 등록 + 재알림
```

---

## 빠른 시작

```bash
git clone https://github.com/HyunDove/github-pr-bot.git
cd github-pr-bot
pip install -r requirements.txt
cp .env.example .env   # .env 편집 후
python bot.py
```

자세한 설치 방법 → [docs/guide.md](docs/guide.md)

---

## 환경변수

| 변수 | 설명 |
|---|---|
| `DISCORD_BOT_TOKEN` | Discord 봇 토큰 |
| `DISCORD_CHANNEL_ID` | 알림 받을 채널 ID |
| `GITHUB_REPO` | 감시할 레포 (예: `owner/repo`) |
| `POLL_INTERVAL` | 폴링 간격(초), 기본값 `30` |

---

## 파일 구조

```
github-pr-bot/
  bot.py            # 메인 — 폴링 루프 및 PR 처리
  config.py         # 환경변수 로드
  review_pr.py      # Claude Code CLI 리뷰 실행
  github_ops.py     # gh CLI 래퍼 (diff, 코멘트, 이슈, 머지)
  discord_notify.py # Discord 메시지 포맷 및 전송
  requirements.txt  # python-dotenv, requests
  .env.example      # 환경변수 템플릿
  docs/
    guide.md        # 상세 설치 가이드
```

---

## Discord 알림 예시

**반려 시:**
```
❌ PR #7 반려
📌 제목: feat: 로그인 기능 추가
👤 작성자: HyunDove

📋 리뷰 요약
SQL Injection 취약점과 하드코딩된 시크릿이 발견되었습니다.

⚠️ 발견된 이슈 (2건)
━━━━━━━━━━━━━━━━━━━
🔴 [치명적] SQL Injection 취약점
❓ 문제: username을 쿼리에 직접 삽입
💡 원인: 파라미터 바인딩 미사용
🔧 해결: cursor.execute("... WHERE username = ?", (username,))
━━━━━━━━━━━━━━━━━━━

🔗 https://github.com/owner/repo/pull/7
```

**승인 시:**
```
✅ PR #8 승인
📌 제목: fix: SQL Injection 수정
👤 작성자: HyunDove

📋 리뷰 요약
보안 취약점이 모두 수정되었습니다. 코드 품질이 양호합니다.

🔗 https://github.com/owner/repo/pull/8
```

---

## 멀티 레포 적용

`bot.py`, `config.py`, `review_pr.py`, `github_ops.py`, `discord_notify.py`, `requirements.txt`를 대상 레포에 복사하고 `.env`의 `GITHUB_REPO`만 변경하면 됩니다.