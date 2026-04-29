# This file holds all configuration for the AI QA Copilot.
# Keeping all config in one place makes it easy to change settings
# without hunting through multiple files.
# All sensitive values like API keys are loaded from environment
# variables so they never get hardcoded into the source code.

import os


# GitHub configuration
# GITHUB_TOKEN: your personal access token for GitHub API access
# GITHUB_REPO: the repository to monitor in "username/repo-name" format
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "ujjwaldahiya399/AI-QA-Copilot-Demo")

# Groq configuration
# GROQ_API_KEY: your free Groq API key for LLaMA access
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# AI model to use for all analysis tasks.
# LLaMA 3.3 70B is the most capable free model on Groq.
GROQ_MODEL = "llama-3.3-70b-versatile"

# Maximum number of characters from the diff to send to the AI.
# We limit this to stay within the model's token limit.
MAX_DIFF_LENGTH = 8000

# Report output path
REPORT_PATH = "reports/report.html"