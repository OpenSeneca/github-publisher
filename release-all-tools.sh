#!/usr/bin/env bash
# Tag and push releases for all OpenSeneca tools

set -e

VERSION=${1:-1.0.0}
TOOLS_DIR="/home/exedev/.openclaw/workspace/tools"
TOOLS="blog-assistant squad-deployer squad-ssh-manager forge-monitor squad-dashboard github-publisher"

echo "🚀 Tagging and pushing releases for version v${VERSION}"
echo ""

for tool in $TOOLS; do
    TOOL_DIR="$TOOLS_DIR/$tool"
    if [ ! -d "$TOOL_DIR/.git" ]; then
        echo "⚠️  Skipping $tool - not a git repository"
        continue
    fi

    echo "📦 Processing $tool..."

    # Check if tag already exists
    if git -C "$TOOL_DIR" tag -l "v${VERSION}" | grep -q "v${VERSION}"; then
        echo "   Tag v${VERSION} already exists, skipping..."
        echo ""
        continue
    fi

    # Create and push tag
    git -C "$TOOL_DIR" tag -a "v${VERSION}" -m "Release v${VERSION}"
    git -C "$TOOL_DIR" push origin "v${VERSION}"

    echo "   ✅ Tagged and pushed v${VERSION}"
    echo ""
done

echo "✅ All tools processed!"
