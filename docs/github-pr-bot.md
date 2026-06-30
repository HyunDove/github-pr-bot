# GitHub PR Review Bot

## 개요

PR 이벤트 발생 시 Claude AI가 코드를 자동 리뷰하고, 결과를 Discord로 알림 + 문제 발견 시 GitHub 이슈 자동 등록하는 봇.

---

## 결정 사항

| 항목 | 결정 |
|---|---|
| 언어 | Python |
| 린터 | 사용 안 함 (Claude API만으로 리뷰) |
| 코드 리뷰 엔진 | Claude API (Anthropic) |
| 알림 채널 | Discord Webhook |
| 배포 방식 | GitHub Actions |
| 멀티레포 전략 | 레포별 복사 (`.github/workflows/pr-review.yml`) |

---

## 아키텍처

```
PR open/sync
     ↓
GitHub Actions 트리거
     ↓
PR diff 추출 (gh api)
     ↓
Claude API 호출 (diff + 리뷰 프롬프트)
     ↓
├─ PR 코멘트 게시
├─ 심각 문제 → GitHub 이슈 자동 생성
└─ Discord Webhook 알림
```

---

## Claude API 비용

- 모델: Claude Sonnet 4.6
- PR 리뷰 1회 기준 약 **$0.005 ~ $0.02**
- 월 PR 100개 기준 약 **$0.5 ~ $2** 수준
- 발급: https://console.anthropic.com → API Keys
- Claude Code 구독과 **별도 청구** (종량제)

---

## 필요한 시크릿 (GitHub Actions Secrets)

| 시크릿 키 | 설명 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API 키 |
| `DISCORD_WEBHOOK_URL` | Discord 채널 Webhook URL |
| `GITHUB_TOKEN` | 자동 제공 (Actions 기본값) |

---

## 구현 예정 파일 구조

```
.github/
  workflows/
    pr-review.yml        # GitHub Actions 워크플로우
scripts/
  review_pr.py           # Claude API 호출 + 이슈 생성 로직
  notify_discord.py      # Discord 알림 로직
```

---

## TODO

- [ ] `review_pr.py` 작성 (diff 추출 → Claude API → PR 코멘트 → 이슈 생성)
- [ ] `notify_discord.py` 작성 (Discord Webhook 알림)
- [ ] `pr-review.yml` 작성 (Actions 트리거 + 스크립트 실행)
- [ ] GitHub Secrets 설정 방법 가이드
- [ ] 테스트 레포에 적용 및 검증

---

## 대화 히스토리 요약

1. PR BOT으로 GitHub 레포 연결 → 코드 품질 검증 → 이슈 등록 가능 여부 확인 → **가능**
2. 린터 없이 Claude만으로 구현 가능 여부 → **가능, 충분**
3. 하나의 레포만 지정 가능한지 → **여러 레포 가능, 레포별 복사 방식 선택**
4. Claude API 결제 → 종량제, PR당 수 센트 수준으로 저렴
5. 레포별 복사 방식으로 진행 결정
