import subprocess


def get_pr_diff(repo: str, pr_number: int) -> str:
    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--repo", repo],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    return result.stdout


def post_pr_comment(repo: str, pr_number: int, body: str):
    subprocess.run(
        ["gh", "pr", "comment", str(pr_number), "--repo", repo, "--body", body],
        check=True,
    )


def create_issue(repo: str, title: str, body: str) -> str:
    result = subprocess.run(
        ["gh", "issue", "create", "--repo", repo,
         "--title", title, "--body", body, "--label", "bug"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    return result.stdout.strip()


def merge_pr(repo: str, pr_number: int):
    subprocess.run(
        ["gh", "pr", "merge", str(pr_number), "--repo", repo, "--merge"],
        check=True,
    )
