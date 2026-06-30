import subprocess
import json
import re

PROMPT_TEMPLATE = """당신은 엄격한 코드 리뷰어입니다. PR의 변경사항을 분석하고 반드시 JSON만 응답하세요.

## PR 정보
- 제목: {title}
- 작성자: {author}
- 설명: {body}

## 변경사항 (diff)
{diff}

## 응답 형식 (JSON만, 다른 텍스트 없이)
{{
  "status": "approved 또는 rejected",
  "summary": "전체 리뷰 요약 1-2문장",
  "issues": [
    {{
      "severity": "critical 또는 warning 또는 info",
      "title": "이슈 제목",
      "description": "구체적인 설명과 수정 방법",
      "create_github_issue": true
    }}
  ],
  "review_comment": "PR에 남길 마크다운 코멘트"
}}

## 판단 기준
- critical: 보안 취약점, 데이터 손실 위험, 런타임 에러 가능성 → status=rejected, create_github_issue=true
- warning: 성능 문제, 코드 품질 미흡 → create_github_issue=false
- info: 개선 제안 → create_github_issue=false
- critical 이슈가 하나라도 있으면 status=rejected, 없으면 status=approved"""


def review_pr(title: str, author: str, body: str, diff: str) -> dict:
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... (diff가 너무 길어 일부 생략됨)"

    prompt = PROMPT_TEMPLATE.format(
        title=title,
        author=author,
        body=body or "(설명 없음)",
        diff=diff,
    )

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=180,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI 오류: {result.stderr}")

    match = re.search(r"\{[\s\S]*\}", result.stdout)
    if not match:
        raise ValueError(f"JSON 파싱 실패: {result.stdout[:300]}")

    return json.loads(match.group())
