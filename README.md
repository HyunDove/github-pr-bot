# GitHub PR Review Bot

Claude AI가 PR을 자동으로 리뷰하고, Discord로 알림을 보내며, 문제 발견 시 GitHub 이슈를 자동 등록하는 봇입니다.

## 아키텍처

```
PR open/sync
     ↓
GitHub Actions 트리거
     ↓
PR diff 추출
     ↓
Claude API 코드 리뷰
     ↓
├─ PR 코멘트 게시
├─ 심각 문제 → GitHub 이슈 자동 생성
└─ Discord Webhook 알림
```

---

## 초기 세팅 방법

### 1. 사전 준비

#### Claude API 키 발급
1. [console.anthropic.com](https://console.anthropic.com) 접속 → 로그인
2. **API Keys** 메뉴 → **Create Key**
3. 생성된 키 복사 (`sk-ant-...` 형태)

#### Discord Webhook URL 발급
1. Discord 알림 받을 채널 → **채널 편집** → **연동** → **웹후크**
2. **새 웹후크** 생성 → **웹후크 URL 복사**

---

### 2. 이 봇을 적용할 레포에 파일 복사

아래 파일들을 대상 레포에 복사합니다.

```
대상 레포/
  .github/
    workflows/
      pr-review.yml       ← 복사
  scripts/
    review_pr.py          ← 복사
    notify_discord.py     ← 복사
  requirements.txt        ← 복사
```

---

### 3. GitHub Secrets 등록

대상 레포의 **Settings → Secrets and variables → Actions → New repository secret** 에서 아래 두 가지를 등록합니다.

| Secret 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API 키 (`sk-ant-...`) |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |

> `GITHUB_TOKEN`은 GitHub Actions에서 자동으로 제공되므로 별도 등록 불필요합니다.

---

### 4. 동작 확인

Secrets 등록 후 PR을 하나 열면 자동으로 봇이 작동합니다.

- PR 탭 → **Checks** 에서 Actions 실행 상태 확인
- PR 코멘트에 Claude 리뷰 결과 게시됨
- Discord 채널에 알림 도착
- 심각한 문제 발견 시 Issues 탭에 자동 등록

---

## 비용

| 항목 | 금액 |
|---|---|
| PR 리뷰 1회 | 약 $0.005 ~ $0.02 |
| 월 100회 기준 | 약 $0.5 ~ $2 |

Claude Code 구독과 별도로 [console.anthropic.com](https://console.anthropic.com) 에서 종량제로 청구됩니다.

---

## 멀티 레포 적용

레포별로 파일을 복사하는 방식으로 여러 레포에 적용할 수 있습니다.
새 레포에 적용할 때마다 **2~3단계**를 반복하면 됩니다.

---

## 파일 구조

```
github-pr-bot/
  README.md                        # 세팅 가이드 (이 파일)
  requirements.txt                 # Python 의존성
  docs/
    github-pr-bot.md               # 기획 및 대화 히스토리
  .github/
    workflows/
      pr-review.yml                # GitHub Actions 워크플로우
  scripts/
    review_pr.py                   # Claude API 리뷰 + 이슈 생성
    notify_discord.py              # Discord 알림
```
