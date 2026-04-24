#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <space_id> [public|private]"
  echo "Example: $0 your-username/BioMind public"
  exit 1
fi

SPACE_ID="$1"
VISIBILITY="${2:-public}"

if ! command -v hf >/dev/null 2>&1; then
  echo "Error: Hugging Face CLI 'hf' is not installed."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed."
  exit 1
fi

if [[ ! -f README.md || ! -f Dockerfile || ! -f pyproject.toml ]]; then
  echo "Error: run this script from the BioMind project root."
  exit 1
fi

if [[ "$VISIBILITY" != "public" && "$VISIBILITY" != "private" ]]; then
  echo "Error: visibility must be 'public' or 'private'."
  exit 1
fi

if ! hf auth whoami >/dev/null 2>&1; then
  echo "Error: Hugging Face CLI is not authenticated. Run 'hf auth login' first."
  exit 1
fi

if [[ ! -d .git ]]; then
  git init
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Prepare BioMind for Hugging Face Spaces deployment"
fi

if ! hf repo create "$SPACE_ID" --type space --space-sdk docker --$VISIBILITY >/dev/null 2>&1; then
  echo "Note: Space may already exist. Continuing with git remote setup."
fi

REMOTE_URL="https://huggingface.co/spaces/$SPACE_ID"

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

git branch -M main
git push -u origin main

echo "Deployed to https://huggingface.co/spaces/$SPACE_ID"
