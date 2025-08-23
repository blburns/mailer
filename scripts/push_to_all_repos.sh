#!/bin/bash

# Script to push to both remote repositories
# Usage: ./scripts/push_all.sh [branch_name]
# Default branch is 'main' if not specified

BRANCH=${1:-main}

echo "Pushing to both remote repositories..."
echo "Branch: $BRANCH"
echo ""

echo "1. Pushing to origin (development repo)..."
git push origin $BRANCH
if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to origin"
else
    echo "❌ Failed to push to origin"
    exit 1
fi

echo ""
echo "2. Pushing to destination (production repo)..."
git push destination $BRANCH
if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to destination"
else
    echo "❌ Failed to push to destination"
    exit 1
fi

echo ""
echo "🎉 Successfully pushed to both repositories!"
echo "Origin: $(git remote get-url origin)"
echo "Destination: $(git remote get-url destination)"
