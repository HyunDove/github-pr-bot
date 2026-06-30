# GitHub PR Review Bot

Claude Code가 PR을 자동으로 리뷰하고, Discord로 결과를 알려주며, 문제 발견 시 GitHub 이슈를 자동 등록하는 봇입니다.
Claude API 키 없이 로컬 Claude Code로 동작합니다.

## 아키텍처

```
PR 오픈
  ↓
GitHub Webhook → Cloudflare Tunnel → 로컬 봇 서버 (bot.py)
  ↓
Claude Code로 코드 리뷰
  ↓
├─ PR 코멘트 게시
├─ critical 이슈 → GitHub 이슈 자동 등록
└─ Discord 채널 메시지 (✅ 승인 / ❌ 반려 + 이유)
```

---

## 파일 구조

```
github-pr-bot/
  bot.py               # 메인 진입점 (Discord 봇 + Webhook 서버)
  config.py            # 환경변수 로드
  webhook_server.py    # GitHub Webhook 수신 (Flask)
  review_pr.py         # Claude Code로 PR 리뷰
  github_ops.py        # PR 코멘트, 이슈 생성 (gh CLI)
  discord_notify.py    # Discord 메시지 빌더
  .env.example         # 환경변수 템플릿
  requirements.txt     # Python 의존성
  docs/
    setup-cloudflare.md  # Cloudflare Tunnel 세팅 가이드
    github-pr-bot.md     # 기획 및 대화 히스토리
```

---

## 초기 세팅 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Discord 봇 생성

1. [discord.com/developers/applications](https://discord.com/developers/applications) 접속
2. **New Application** → 이름 입력 → **Create**
3. 좌측 **Bot** → **Add Bot**
4. **Token** 복사 → `.env`의 `DISCORD_BOT_TOKEN`에 입력
5. **OAuth2 → URL Generator** → `bot` 체크 → `Send Messages` 권한 체크
6. 생성된 URL로 봇을 Discord 서버에 초대

### 3. Discord 채널 ID 확인

1. Discord 설정 → **고급** → **개발자 모드** 활성화
2. 알림 받을 채널 우클릭 → **ID 복사**
3. `.env`의 `DISCORD_CHANNEL_ID`에 입력

### 4. 환경변수 설정

`.env.example`을 복사해 `.env` 파일 생성:

```bash
cp .env.example .env
```

| 변수 | 설명 |
|---|---|
| `DISCORD_BOT_TOKEN` | Discord 봇 토큰 |
| `DISCORD_CHANNEL_ID` | 알림 받을 채널 ID |
| `GITHUB_WEBHOOK_SECRET` | Webhook 서명 검증용 임의 문자열 |
| `PORT` | 로컬 서버 포트 (기본: 8080) |

### 5. Cloudflare Tunnel 설정

→ [docs/setup-cloudflare.md](docs/setup-cloudflare.md) 참고

### 6. GitHub Webhook 등록

대상 레포 → **Settings → Webhooks → Add webhook**

| 항목 | 값 |
|---|---|
| Payload URL | `https://<터널 URL>/webhook` |
| Content type | `application/json` |
| Secret | `.env`의 `GITHUB_WEBHOOK_SECRET` 값 |
| Trigger | Pull requests |

---

## 실행

```bash
# 터미널 1: Cloudflare Tunnel
cloudflared tunnel run pr-bot

# 터미널 2: 봇 실행
python bot.py
```

---

## Discord 메시지 예시

**승인:**
```
✅ PR #12 승인
제목: Fix login bug
작성자: HyunDove

요약
로그인 관련 버그를 수정했습니다. 코드 품질이 양호합니다.

🔗 https://github.com/owner/repo/pull/12
```

**반려:**
```
❌ PR #13 반려
제목: Add payment feature
작성자: HyunDove

요약
결제 로직에 보안 취약점이 발견되었습니다.

발견된 이슈
🔴 SQL Injection 취약점
🟡 에러 처리 누락

등록된 GitHub 이슈
• https://github.com/owner/repo/issues/45

🔗 https://github.com/owner/repo/pull/13
```

---

## 멀티 레포 적용

`bot.py`, `config.py`, `webhook_server.py`, `review_pr.py`, `github_ops.py`, `discord_notify.py`, `requirements.txt`를 대상 레포에 복사하고, GitHub Webhook만 새로 등록하면 됩니다.
