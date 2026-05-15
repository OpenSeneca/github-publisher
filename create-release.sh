#!/bin/bash
# create-release.sh - Automates GitHub releases for OpenSeneca tools
# Reads version from setup.py, generates changelog from git commits, and publishes release via GitHub API

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
VERSION_FILE="$REPO_ROOT/setup.py"
CHANGELOG_FILE="$REPO_ROOT/CHANGELOG.md"
ASSET_DIR="$REPO_ROOT/dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check required tools
check_requirements() {
    if ! command -v gh &> /dev/null; then
        log_error "gh CLI not found. Install from https://cli.github.com/"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        log_error "git not found"
        exit 1
    fi
}

# Get version from setup.py
get_version() {
    if [ ! -f "$VERSION_FILE" ]; then
        log_error "setup.py not found at $VERSION_FILE"
        exit 1
    fi

    VERSION=$(grep -oP "version=\K['\"][^'\"]+['\"]" "$VERSION_FILE" | tr -d "'" | tr -d '"' | head -1)
    if [ -z "$VERSION" ]; then
        log_error "Could not extract version from setup.py"
        exit 1
    fi

    log_info "Detected version: $VERSION"
    echo "$VERSION"
}

# Generate changelog from git commits
generate_changelog() {
    local prev_tag
    prev_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

    if [ -z "$prev_tag" ]; then
        log_info "No previous tags found. Using all commits."
        COMMITS=$(git log --pretty=format:"- %s (%h)" main)
    else
        log_info "Changes since $prev_tag:"
        COMMITS=$(git log --pretty=format:"- %s (%h)" "$prev_tag"..main)
    fi

    if [ -z "$COMMITS" ]; then
        log_warn "No commits found since last release"
        return 1
    fi

    echo "$COMMITS"
}

# Create GitHub release
create_release() {
    local version="$1"
    local changelog="$2"
    local repo_name

    repo_name=$(git config --get remote.origin.url | sed -E 's/.*github.com[/:]([^/]+\/[^/]+)\.git/\1/')
    if [ -z "$repo_name" ]; then
        log_error "Could not determine GitHub repository name"
        exit 1
    fi

    log_info "Creating release $version for $repo_name"

    # Create release notes
    local release_notes
    release_notes="## Release $VERSION

$changelog

### Installation
\`\`\`bash
pip install $(python setup.py --name)
\`\`\`
"

    # Check if release already exists
    if gh release view "$version" --repo "$repo_name" &>/dev/null; then
        log_warn "Release $version already exists. Skipping."
        return 0
    fi

    # Create release
    if gh release create "$version" \
        --title "Release $VERSION" \
        --notes "$release_notes" \
        --repo "$repo_name"; then
        log_info "Release $version created successfully"

        # Upload assets
        if [ -d "$ASSET_DIR" ] && [ "$(ls -A "$ASSET_DIR" 2>/dev/null)" ]; then
            log_info "Uploading assets from $ASSET_DIR"
            gh release upload "$version" "$ASSET_DIR"/* --repo "$repo_name"
        fi

        return 0
    else
        log_error "Failed to create release"
        return 1
    fi
}

# Main execution
main() {
    check_requirements

    VERSION=$(get_version)
    CHANGELOG=$(generate_changelog)

    if [ -z "$CHANGELOG" ]; then
        log_error "No changes to release"
        exit 1
    fi

    log_info "Changelog:"
    echo "$CHANGELOG"
    echo

    read -p "Proceed with release $VERSION? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release cancelled"
        exit 0
    fi

    create_release "$VERSION" "$CHANGELOG"

    if [ $? -eq 0 ]; then
        log_info "Release $VERSION completed successfully"
    else
        log_error "Release failed"
        exit 1
    fi
}

main "$@"