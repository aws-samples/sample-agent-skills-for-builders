#!/bin/bash
# Push converted content to GitLab Wiki repo.
# Usage: push_to_wiki.sh <wiki_git_url> <page_path> <content_dir> <quip_url>

set -euo pipefail

WIKI_URL="$1"
PAGE_PATH="$2"
CONTENT_DIR="$3"
QUIP_URL="${4:-}"

# Input validation
if [[ -z "$WIKI_URL" || -z "$PAGE_PATH" || -z "$CONTENT_DIR" ]]; then
    echo "Usage: $0 <wiki_git_url> <page_path> <content_dir> [quip_url]"
    exit 1
fi

# Validate wiki URL format (git SSH or HTTPS only)
if ! [[ "$WIKI_URL" =~ ^(git@|https://) ]]; then
    echo "ERROR: Invalid wiki URL format. Must start with git@ or https://"
    exit 1
fi

# Validate page path (no .. traversal)
if [[ "$PAGE_PATH" == *".."* ]]; then
    echo "ERROR: Page path must not contain '..'"
    exit 1
fi

# Sanitize QUIP_URL for safe use in commit messages (strip anything suspicious)
SAFE_QUIP_URL=$(echo "$QUIP_URL" | sed 's/[^a-zA-Z0-9:/_?#.=-]//g')

WORK_DIR=$(mktemp -d)
if [[ -z "$WORK_DIR" || ! "$WORK_DIR" == /tmp/* ]]; then
    echo "ERROR: Failed to create secure temp directory"
    exit 1
fi
trap "rm -rf '$WORK_DIR'" EXIT

echo "Cloning wiki repo..."
git clone "$WIKI_URL" "$WORK_DIR/wiki" 2>&1 | tail -1

cd "$WORK_DIR/wiki"

# Determine image path prefix based on page depth
PAGE_DIR=$(dirname "$PAGE_PATH")
if [ "$PAGE_DIR" = "." ]; then
    IMG_PREFIX="uploads"
else
    DEPTH=$(echo "$PAGE_DIR" | tr '/' '\n' | wc -l)
    IMG_PREFIX=""
    for i in $(seq 1 "$DEPTH"); do IMG_PREFIX="../${IMG_PREFIX}"; done
    IMG_PREFIX="${IMG_PREFIX}uploads"
fi

# Copy uploads
mkdir -p uploads
if [ -d "$CONTENT_DIR/uploads" ]; then
    cp "$CONTENT_DIR/uploads/"* uploads/ 2>/dev/null || true
    echo "Copied $(ls uploads/ | wc -l) assets"
fi

# Create page directory if needed
mkdir -p "$(dirname "${PAGE_PATH}.md")"

# Copy content with adjusted image paths
sed "s|uploads/|${IMG_PREFIX}/|g" "$CONTENT_DIR/content.md" > "${PAGE_PATH}.md"

# Append source attribution
if [ -n "$SAFE_QUIP_URL" ]; then
    printf '\n---\n> **Source**: Migrated from [Quip](%s)\n' "$SAFE_QUIP_URL" >> "${PAGE_PATH}.md"
fi

echo "Created: ${PAGE_PATH}.md"

# Commit and push
git add -A
git commit -m "Add ${PAGE_PATH} from Quip" 2>&1 | head -3
git push origin main 2>&1 | tail -3
echo "Pushed to wiki successfully"
