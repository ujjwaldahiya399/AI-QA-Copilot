# This file handles all communication with the GitHub API.
# It connects to GitHub, fetches pull requests from a repository,
# extracts the code diff from each PR, and posts the QA report
# back as a comment on the PR so the developer sees it immediately.

from github import Github
from config import GITHUB_TOKEN, GITHUB_REPO


def connect_to_github():
    # Create a connection to GitHub using the personal access token.
    # The Github() object is our gateway to everything on GitHub —
    # repositories, pull requests, comments, and more.
    print("[GITHUB] Connecting to GitHub...")
    client = Github(GITHUB_TOKEN)
    print("[GITHUB] Connected successfully.")
    return client


def get_open_pull_requests(client):
    # Fetch all open pull requests from the configured repository.
    # Returns a list of PR objects we can loop through and analyze.

    print(f"[GITHUB] Fetching open PRs from {GITHUB_REPO}...")

    # Get the repository object using the "username/repo-name" format.
    repo = client.get_repo(GITHUB_REPO)

    # Get all pull requests with state "open".
    # This returns only PRs that are currently open — not merged or closed.
    open_prs = list(repo.get_pulls(state="open"))

    print(f"[GITHUB] Found {len(open_prs)} open PR(s).")
    return open_prs

def get_pr_diff(pr):
    # Extract the code diff from a pull request.
    # The diff shows exactly what lines of code were added or removed.
    # This is what we send to the AI for analysis.

    print(f"[GITHUB] Fetching diff for PR #{pr.number}: {pr.title}")

    # Get all files changed in this PR.
    files = pr.get_files()

    # Build a combined diff string from all changed files.
    # We include the filename and the patch (the actual diff) for each file.
    diff_text = ""
    for file in files:

        # Add the filename as a header so the AI knows which file changed.
        diff_text += f"\n--- File: {file.filename} ---\n"

        # file.patch contains the actual diff in unified diff format.
        # Lines starting with + are additions, lines with - are removals.
        # Some files like images have no patch so we handle that gracefully.
        if file.patch:
            diff_text += file.patch
        else:
            diff_text += "[Binary file or no changes]"

    return diff_text

def get_pr_details(pr):
    # Extract key details from a pull request object.
    # Returns a clean dictionary with the most useful PR information.

    return {
        "number": pr.number,
        "title": pr.title,
        "author": pr.user.login,
        "body": pr.body or "No description provided",
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
        "url": pr.html_url,
        "created_at": str(pr.created_at),
        "changed_files": pr.changed_files,
        "additions": pr.additions,
        "deletions": pr.deletions
    }


def post_pr_comment(client, pr_number, comment_body):
    # Post the QA report as a comment on the pull request.
    # This is what makes the copilot feel like a real team member —
    # the developer opens their PR and sees the AI QA report waiting for them.

    print(f"[GITHUB] Posting QA report as comment on PR #{pr_number}...")

    # Get the repository object.
    repo = client.get_repo(GITHUB_REPO)

    # Get the specific PR by its number.
    pr = repo.get_pull(pr_number)

    # Create a comment on the PR with the report content.
    pr.create_issue_comment(comment_body)

    print(f"[GITHUB] Comment posted successfully on PR #{pr_number}.")