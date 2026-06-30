# Cloudflare Tunnel 세팅 가이드

로컬 봇 서버를 GitHub Webhook과 연결하기 위해 Cloudflare Tunnel을 사용합니다.

---

## 1. cloudflared 설치

```bash
winget install Cloudflare.cloudflared
```

설치 확인:
```bash
cloudflared --version
```

---

## 2. Cloudflare 계정 로그인

```bash
cloudflared tunnel login
```

브라우저가 열리면 Cloudflare 계정으로 로그인 → 도메인 선택 → 인증 완료.

---

## 3. 터널 생성

```bash
cloudflared tunnel create pr-bot
```

출력 예시:
```
Created tunnel pr-bot with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

터널 ID를 메모해 둡니다.

---

## 4. 설정 파일 생성

`~/.cloudflared/config.yml` 파일 생성:

```yaml
tunnel: <터널 ID>
credentials-file: C:\Users\<사용자명>\.cloudflared\<터널 ID>.json

ingress:
  - service: http://localhost:8080
```

> 도메인이 없어도 됩니다. 도메인 없이 사용하면 Cloudflare가 임시 URL을 제공합니다.

---

## 5. 터널 실행

```bash
cloudflared tunnel run pr-bot
```

출력에서 URL을 확인합니다:
```
https://pr-bot.trycloudflare.com
```

---

## 6. GitHub Webhook 등록

1. 대상 GitHub 레포 → **Settings → Webhooks → Add webhook**
2. **Payload URL**: `https://pr-bot.trycloudflare.com/webhook`
3. **Content type**: `application/json`
4. **Secret**: `.env`의 `GITHUB_WEBHOOK_SECRET` 값과 동일하게 입력
5. **Trigger**: `Pull requests` 체크
6. **Add webhook** 클릭

---

## 7. 봇 실행 순서

매번 아래 순서로 실행합니다:

```bash
# 1. Cloudflare Tunnel 실행 (별도 터미널)
cloudflared tunnel run pr-bot

# 2. PR 봇 실행
python bot.py
```
