# GitHub PR Review Bot — 로컬 설치 가이드

Claude Code CLI를 사용해 PR을 자동 리뷰하고, Discord로 결과를 알려주며, 문제 발견 시 GitHub 이슈를 자동 등록하는 봇입니다.
**Claude API 키 없이**, **터널 없이** 로컬에서만 실행됩니다.

---

## 동작 방식

```
bot.py가 30초마다 GitHub API 폴링
  └─ 새 PR 발견
       ├─ Claude Code로 코드 리뷰 (claude -p)
       ├─ PR에 리뷰 코멘트 게시
       ├─ critical 이슈 → GitHub 이슈 자동 등록
       ├─ 승인 → PR 자동 머지
       └─ Discord 채널에 결과 알림

개발자가 코드 수정 후 새 커밋 push
  └─ 커밋 SHA 변경 감지 → 자동 재검증
       ├─ 이슈 없음 → GitHub 이슈 close + PR 머지
       └─ 이슈 있음 → 새 이슈 등록 + Discord 재알림
```

---

## 사전 준비

| 항목 | 확인 |
|---|---|
| Python 3.10 이상 | `python --version` |
| Claude Code CLI | `claude --version` (로그인 상태여야 함) |
| GitHub CLI | `gh --version` + `gh auth login` 완료 |

---

## 1단계 — 레포 클론 및 의존성 설치

```bash
git clone https://github.com/HyunDove/github-pr-bot.git
cd github-pr-bot
pip install -r requirements.txt
```

---

## 2단계 — Discord 봇 생성

1. [discord.com/developers/applications](https://discord.com/developers/applications) 접속
2. **New Application** → 이름 입력 (예: `PR Bot`) → **Create**
3. 좌측 메뉴 **Bot** 클릭
4. **Token** → **Reset Token** → 복사해 둠
5. 아래로 스크롤 → **MESSAGE CONTENT INTENT** 활성화 → **Save Changes**

### 봇을 서버에 초대

1. 좌측 메뉴 **OAuth2 → URL Generator**
2. Scopes: `bot` 체크
3. Bot Permissions: `Send Messages` 체크
4. 생성된 URL을 복사해 브라우저에서 열기 → 서버 선택 후 초대

### 채널 ID 확인

1. Discord 설정 → **고급** → **개발자 모드** 활성화
2. 알림 받을 채널 **우클릭** → **ID 복사**

> ⚠️ **주의**: 채널 ID와 서버 ID는 다릅니다. 반드시 채널을 우클릭해서 복사하세요.

---

## 3단계 — 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채웁니다:

```env
DISCORD_BOT_TOKEN=발급받은_봇_토큰
DISCORD_CHANNEL_ID=알림받을_채널_ID
GITHUB_REPO=owner/repo-name
POLL_INTERVAL=30
```

| 변수 | 설명 | 예시 |
|---|---|---|
| `DISCORD_BOT_TOKEN` | Discord 봇 토큰 | `MTUy...` |
| `DISCORD_CHANNEL_ID` | 알림 채널 ID (채널 우클릭 → ID 복사) | `1521351579960213516` |
| `GITHUB_REPO` | 감시할 GitHub 레포 | `HyunDove/my-project` |
| `POLL_INTERVAL` | 폴링 간격(초), 기본값 30 | `30` |

---

## 4단계 — GitHub CLI 인증 확인

```bash
gh auth status
```

`Logged in to github.com` 메시지가 나오면 정상입니다.
안 되어 있으면:

```bash
gh auth login
```

---

## 5단계 — 봇 실행

```bash
python bot.py
```

정상 실행 시 터미널 출력:

```
[Bot] 폴링 시작 - HyunDove/my-project (30초 간격)
[Bot] 추적 중인 PR: []
[Bot] 새 PR 없음 (열린 PR: 0개)
```

---

## 전체 동작 예시

### PR 반려 (critical 이슈 발견)

```
[Bot] PR #7 신규 리뷰 시작: feat: 로그인 기능 추가
[Bot] PR #7 코멘트 등록 완료
[Bot] 이슈 등록: https://github.com/owner/repo/issues/12
[Discord] PR #7 알림 전송 완료
```

Discord 메시지:
```
❌ PR #7 반려
📌 제목: feat: 로그인 기능 추가
👤 작성자: HyunDove

📋 리뷰 요약
SQL Injection 취약점과 하드코딩된 시크릿이 발견되었습니다.

⚠️ 발견된 이슈 (2건)
━━━━━━━━━━━━━━━━━━━
🔴 [치명적] SQL Injection 취약점
❓ 문제: username을 쿼리에 직접 삽입하고 있음
💡 원인: 파라미터 바인딩 미사용
🔧 해결: cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

🔴 [치명적] 하드코딩된 시크릿
❓ 문제: API 키가 소스코드에 노출됨
💡 원인: 환경변수 미사용
🔧 해결: os.getenv("API_KEY")로 환경변수에서 읽어오기
━━━━━━━━━━━━━━━━━━━

🔗 https://github.com/owner/repo/pull/7
```

### 코드 수정 후 재검증 → 승인

```
[Bot] PR #7 새 커밋 감지 - 재검증 시작
[Bot] PR #7 코멘트 등록 완료
[Bot] GitHub 이슈 #12 close 완료
[Bot] PR #7 자동 머지 완료
[Discord] PR #7 알림 전송 완료
```

---

## 멀티 레포 적용

다른 레포에도 봇을 적용하려면:

1. 아래 파일들을 대상 레포에 복사
   ```
   bot.py, config.py, review_pr.py, github_ops.py, discord_notify.py, requirements.txt
   ```
2. `.env`의 `GITHUB_REPO` 값만 변경
3. `python bot.py` 재실행

---

## 파일 구조

```
github-pr-bot/
  bot.py            # 메인 진입점 — 폴링 루프, PR 처리 오케스트레이션
  config.py         # 환경변수 로드
  review_pr.py      # Claude Code CLI로 PR 리뷰 (claude -p)
  github_ops.py     # gh CLI 래퍼 (PR diff, 코멘트, 이슈, 머지)
  discord_notify.py # Discord 메시지 포맷 + Bot Token 전송
  requirements.txt  # Python 의존성 (python-dotenv, requests)
  .env              # 환경변수 (gitignore됨)
  .env.example      # 환경변수 템플릿
  pr_state.json     # PR 추적 상태 (자동 생성, gitignore됨)
  docs/
    guide.md        # 이 파일
```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `[ERROR] 폴링 실패` | gh CLI 인증 만료 | `gh auth login` 재실행 |
| Discord 메시지 404 | 채널 ID가 서버 ID로 잘못 설정됨 | 채널 우클릭 → ID 복사 |
| Discord 메시지 403 | 봇이 서버에 없음 | OAuth2 URL로 서버 초대 |
| Claude 리뷰 안 됨 | Claude Code 미로그인 | `claude` 실행 후 로그인 |
| `KeyError` 오류 | pr_state.json 포맷 불일치 | `pr_state.json` 삭제 후 재시작 |