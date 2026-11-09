#!/bin/sh
# Run once per computer, from the repository root.
cd "$(git rev-parse --show-toplevel)" || exit 1
chmod +x tools/hooks/pre-commit
git config core.hooksPath tools/hooks
echo "Hooks installed: commits with files over 95 MB will be refused."
