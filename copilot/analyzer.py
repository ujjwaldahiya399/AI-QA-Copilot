# This file contains the AI brain of the QA Copilot.
# It takes a code diff from a pull request and uses LLaMA via Groq
# to generate targeted test cases, identify risk areas, and recommend
# what types of testing should be performed for those specific changes.

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_DIFF_LENGTH


# Connect to Groq using the API key from config.
client = Groq(api_key=GROQ_API_KEY)
def generate_test_cases(pr_details, diff_text):
    # Generate targeted test cases based on the actual code changes in the PR.
    # Unlike Project 1 which read from a requirements document,
    # this reads the real code diff — making test cases much more precise
    # and directly relevant to what actually changed.

    print("[ANALYZER] Generating test cases from PR diff...")

    # Trim the diff to stay within the model's token limit.
    # Very large PRs can have thousands of lines of diff.
    trimmed_diff = diff_text[:MAX_DIFF_LENGTH]

    prompt = f"""
You are an expert QA Engineer and SDET reviewing a GitHub Pull Request.

Pull Request Details:
- Title: {pr_details['title']}
- Author: {pr_details['author']}
- Files Changed: {pr_details['changed_files']}
- Lines Added: {pr_details['additions']}
- Lines Removed: {pr_details['deletions']}
- Description: {pr_details['body']}

Code Diff:
{trimmed_diff}

Based on the code changes above, generate exactly 6 targeted test cases.
Include:
- 2 positive test cases (happy path scenarios)
- 2 negative test cases (invalid input or error scenarios)
- 1 edge case (boundary or extreme value)
- 1 security test case (injection, authentication, or authorization)

For each test case provide:
- ID: TC_001, TC_002, etc.
- Title: Short descriptive title
- Type: Positive / Negative / Edge Case / Security
- Steps: numbered steps
- Expected Result: what should happen

Format each test case clearly separated by a line of dashes (---).
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    test_cases = response.choices[0].message.content.strip()
    print("[ANALYZER] Test cases generated successfully.")
    return test_cases


def analyze_risk(pr_details, diff_text):
    # Analyze the PR diff to identify risk areas and recommend
    # what types of testing are most critical for these changes.
    # This helps the QA team prioritize their testing effort.

    print("[ANALYZER] Analyzing risk level of PR changes...")

    trimmed_diff = diff_text[:MAX_DIFF_LENGTH]

    prompt = f"""
You are a senior QA Engineer assessing the risk of a GitHub Pull Request.

Pull Request Details:
- Title: {pr_details['title']}
- Author: {pr_details['author']}
- Files Changed: {pr_details['changed_files']}
- Lines Added: {pr_details['additions']}
- Lines Removed: {pr_details['deletions']}
- Description: {pr_details['body']}

Code Diff:
{trimmed_diff}

Please provide a risk assessment with the following sections:

RISK_LEVEL: [LOW or MEDIUM or HIGH]
RISK_REASONS: [reason 1] | [reason 2] | [reason 3]
TESTING_TYPES: [list the types of testing needed e.g. Unit, Integration, UI, Security, Performance]
CRITICAL_AREAS: [the most important areas to focus testing on]
QUALITY_SCORE: [a score from 1-10 on how well the PR is structured for testing]
SUMMARY: [2-3 sentence overall assessment of this PR from a QA perspective]
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    print("[ANALYZER] Risk analysis complete.")
    return parse_risk_analysis(raw)


def parse_risk_analysis(raw_response):
    # Parse the structured risk analysis response into a clean dictionary.

    def extract_field(label, text):
        for line in text.split("\n"):
            if line.startswith(label):
                return line.replace(label, "").strip()
        return "Not provided"

    risk_level = extract_field("RISK_LEVEL:", raw_response)
    risk_reasons_raw = extract_field("RISK_REASONS:", raw_response)
    testing_types = extract_field("TESTING_TYPES:", raw_response)
    critical_areas = extract_field("CRITICAL_AREAS:", raw_response)
    quality_score = extract_field("QUALITY_SCORE:", raw_response)
    summary = extract_field("SUMMARY:", raw_response)

    # Split risk reasons into a list using | as separator.
    risk_reasons = [r.strip() for r in risk_reasons_raw.split("|") if r.strip()]

    return {
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "testing_types": testing_types,
        "critical_areas": critical_areas,
        "quality_score": quality_score,
        "summary": summary,
        "raw_response": raw_response
    }