"""
Generate a meaningful git commit message using the Claude API.
Reads the staged diff and asks Claude to summarize what changed and why.

Usage (called by the Stop hook):
    python scripts/gen_commit_msg.py
    → prints a single commit message to stdout
"""

import subprocess
import sys
import os
import anthropic

# Load API key from .env file if not already in environment
if not os.environ.get("ANTHROPIC_API_KEY"):
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip('"')
                    break

MAX_DIFF_CHARS = 8000  # Truncate very large diffs to save tokens


def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat", "--diff-filter=AMDRC"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    stat = result.stdout.strip()

    result = subprocess.run(
        ["git", "diff", "--cached", "--diff-filter=AMDRC"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    diff = result.stdout.strip()

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n... (diff truncated)"

    return stat, diff


def generate_message(stat, diff):
    client = anthropic.Anthropic()

    prompt = f"""You are writing a git commit message for a heatmap/GPS trajectory visualization project.

Here is what changed (git diff --stat):
{stat}

Here is the actual diff:
{diff}

Write a concise, single-line commit message (under 72 characters) that:
- Starts with an action verb (add, update, fix, remove, refactor, etc.)
- Describes WHAT changed and briefly WHY or what it achieves
- Is specific enough to understand the change at a glance

Reply with ONLY the commit message, no quotes, no explanation."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


if __name__ == "__main__":
    stat, diff = get_staged_diff()
    if not diff:
        print("no changes")
        sys.exit(0)

    msg = generate_message(stat, diff)
    print(msg)
