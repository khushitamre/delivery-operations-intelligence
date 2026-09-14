#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/khushitamre/delivery-operations-intelligence.git"

required=(app.py download_data.py prepare_data.py validate_data.py requirements.txt README.md .gitignore)
for file in "${required[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "ERROR: Missing required file: $file"
    echo "Run this script from the project root after extracting the GitHub-ready package."
    exit 1
  fi
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# Never commit the large public dataset or generated data mart.
git rm -r --cached --ignore-unmatch data/raw data/processed >/dev/null 2>&1 || true
git rm --cached --ignore-unmatch data/delivery_ops.db >/dev/null 2>&1 || true

git add .
if ! git diff --cached --quiet; then
  git commit -m "Update delivery operations intelligence project"
else
  echo "Local files are already committed."
fi

if ! git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  echo "Remote main branch is empty; pushing initial commit."
else
  echo "Merging existing remote main safely..."
  git fetch origin main
  git merge origin/main --allow-unrelated-histories -X ours -m "Merge existing GitHub repository history" || {
    echo "ERROR: Merge needs manual resolution. Run: git status"
    exit 1
  }
fi

git push -u origin main
echo "SUCCESS: https://github.com/khushitamre/delivery-operations-intelligence"
