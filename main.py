# It ties all the components together and runs the full pipeline:
# 1. Connect to GitHub and fetch open pull requests
# 2. Extract the code diff from each PR
# 3. Generate test cases using AI
# 4. Analyze the risk level using AI
# 5. Generate an HTML report and a PR comment
# 6. Post the report as a comment on the PR
# 7. Save the HTML report locally

import os
from copilot.github_client import (
    connect_to_github,
    get_open_pull_requests,
    get_pr_diff,
    get_pr_details,
    post_pr_comment
)
from copilot.analyzer import generate_test_cases, analyze_risk
from copilot.reporter import generate_html_report, generate_pr_comment
from config import REPORT_PATH


def process_pull_request(client, pr):
    # Process a single pull request through the full AI QA pipeline.
    # This function is called for each open PR found in the repository.

    print(f"\n{'='*60}")
    print(f"[COPILOT] Processing PR #{pr.number}: {pr.title}")
    print(f"{'='*60}")

    # Step 1: Extract PR details and code diff.
    pr_details = get_pr_details(pr)
    diff_text = get_pr_diff(pr)

    if not diff_text.strip():
        print(f"[COPILOT] No diff found for PR #{pr.number}. Skipping.")
        return

    print(f"[COPILOT] PR has {pr_details['changed_files']} changed files.")
    print(f"[COPILOT] +{pr_details['additions']} additions, -{pr_details['deletions']} deletions.")

    # Step 2: Generate targeted test cases from the diff using AI.
    test_cases = generate_test_cases(pr_details, diff_text)

    # Step 3: Analyze the risk level of the changes using AI.
    risk_analysis = analyze_risk(pr_details, diff_text)

    print(f"[COPILOT] Risk Level: {risk_analysis['risk_level']}")
    print(f"[COPILOT] Quality Score: {risk_analysis['quality_score']}/10")

    # Step 4: Generate the HTML report for local viewing.
    html_report = generate_html_report(pr_details, test_cases, risk_analysis)

    # Save the HTML report to the reports folder.
    os.makedirs("reports", exist_ok=True)
    report_file = f"reports/pr_{pr_details['number']}_report.html"
    with open(report_file, "w") as f:
        f.write(html_report)
    print(f"[COPILOT] HTML report saved to {report_file}")

    # Step 5: Generate the markdown comment for GitHub.
    pr_comment = generate_pr_comment(pr_details, test_cases, risk_analysis)

    # Step 6: Post the report as a comment on the PR.
    post_pr_comment(client, pr_details['number'], pr_comment)

    # Step 7: Open the HTML report in the browser.
    os.system(f"open {report_file}")

    print(f"\n[COPILOT] PR #{pr.number} processing complete!")
    return {
        "pr_number": pr_details['number'],
        "pr_title": pr_details['title'],
        "risk_level": risk_analysis['risk_level'],
        "quality_score": risk_analysis['quality_score'],
        "report_file": report_file
    }


def main():
    # Main entry point — runs the full AI QA Copilot pipeline.

    print("\n" + "="*60)
    print("   AI QA COPILOT - Powered by LLaMA 3.3 via Groq")
    print("="*60 + "\n")

    # Step 1: Connect to GitHub.
    client = connect_to_github()

    # Step 2: Fetch all open pull requests.
    open_prs = get_open_pull_requests(client)

    if not open_prs:
        print("[COPILOT] No open pull requests found.")
        print("[COPILOT] Create a PR on your demo repo and run again.")
        return

    # Step 3: Process each open PR through the full pipeline.
    results = []
    for pr in open_prs:
        result = process_pull_request(client, pr)
        if result:
            results.append(result)

    # Step 4: Print a final summary of all PRs processed.
    print("\n" + "="*60)
    print("[COPILOT] FINAL SUMMARY")
    print("="*60)
    print(f"Total PRs processed: {len(results)}")
    for r in results:
        print(f"  PR #{r['pr_number']}: {r['pr_title']}")
        print(f"    Risk: {r['risk_level']} | Score: {r['quality_score']}/10")
        print(f"    Report: {r['report_file']}")

    print("\n[COPILOT] All done!")


if __name__ == "__main__":
    main()