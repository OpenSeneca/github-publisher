#!/bin/bash
# GitHub Publisher - Publish a tool to GitHub (no SSH required)

TOOL_NAME="${1:-squad-deployment-config-fixer}"
VERSION="1.0.0"
GITHUB_ORG="OpenSeneca"
GITHUB_REPO="${GITHUB_ORG}/${TOOL_NAME}"
WORKSPACE="/home/exedev/.openclaw/workspace/tools"

echo "📦 Publishing ${TOOL_NAME} v${VERSION} to GitHub..."

TOOL_DIR="${WORKSPACE}/${TOOL_NAME}"
if [ ! -d "${TOOL_DIR}" ]; then
    echo "❌ Tool directory not found: ${TOOL_DIR}"
    exit 1
fi

cd "${TOOL_DIR}"

# Build distribution
echo "Building distribution..."
rm -rf build dist *.egg-info 2>/dev/null
python3 -m build 2>&1 | tail -5

echo ""
echo "✅ ${TOOL_NAME} v${VERSION} built successfully!"
echo ""
echo "📋 To publish to GitHub manually:"
echo "   1. Create repo: https://github.com/new"
echo "   2. Repository name: ${TOOL_NAME}"
echo "   3. Upload dist/*.whl and dist/*.tar.gz to release"
echo "   4. Create release: v${VERSION}"
echo ""
echo "📍 Distribution files:"
ls -lh dist/