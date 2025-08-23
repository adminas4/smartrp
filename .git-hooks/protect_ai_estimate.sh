#!/usr/bin/env bash
# Blokuoja commit, jei stage'intas backend/app/services/ai_estimate.py
if git diff --cached --name-only | grep -q '^backend/app/services/ai_estimate.py$'; then
  echo "❌ Commit blocked: ai_estimate.py protected."
  exit 1
fi
exit 0
