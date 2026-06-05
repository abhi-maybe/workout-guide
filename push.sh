#!/bin/bash
set -e
cd /tmp/workout-pages
export PATH="/opt/data/bin:$PATH"

TOKEN=$(grep '^GITHUB_TOKEN=' /opt/data/.env | cut -d= -f2)
REMOTE="https://x-access-token:${TOKEN}@github.com/abhi-maybe/workout-guide.git"

git checkout --orphan clean
git add index.html
git commit -m "workout guide"
git branch -D master
git branch -m master
git remote set-url origin "$REMOTE"
git push --force origin master
echo "Done - history rewritten"
