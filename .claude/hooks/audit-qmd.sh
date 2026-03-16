#!/bin/bash
# Runs course architecture audit after any .qmd file is edited.
# Checks for broken links, temporal content on website, stale LMS refs.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run audit if a .qmd file was modified
if [[ "$FILE_PATH" == *.qmd ]]; then
  cd "$CLAUDE_PROJECT_DIR" || exit 0
  python3 scripts/audit_course.py 2>&1
fi

exit 0
