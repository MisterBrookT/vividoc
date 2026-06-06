#!/usr/bin/env bash
set -euo pipefail

REPO="MisterBrookT/vividoc"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/.claude/commands"
COMMANDS_DIR="${HOME}/.claude/commands"

echo "Installing ViviDoc skills for Claude Code..."

mkdir -p "${COMMANDS_DIR}"

for skill in vividoc vividoc-learn vividoc-slides; do
  echo "  → /${skill}"
  curl -fsSL "${BASE_URL}/${skill}.md" -o "${COMMANDS_DIR}/${skill}.md"
done

echo ""
echo "✅ Done. Open any project in Claude Code and run:"
echo ""
echo "   /vividoc Fourier Transform"
echo ""
echo "Or distill an existing explorable explanation:"
echo ""
echo "   /vividoc-learn https://ncase.me/trust/"
echo ""
echo "Or convert lecture slides into an interactive document:"
echo ""
echo "   /vividoc-slides https://example.edu/lecture.pdf"
echo ""
