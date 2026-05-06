#!/usr/bin/env bash
# GitHub Publisher for OpenSeneca Tools
# Automates publishing tools to OpenSeneca GitHub organization

set -e

TOOL_NAME=""
DESCRIPTION=""
VERSION="1.0.0"
GITHUB_ORG="OpenSeneca"
DRY_RUN=false

help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -n, --name NAME          Tool name (required)"
    echo "  -d, --description DESC  Tool description"
    echo "  -v, --version VERSION    Version (default: 1.0.0)"
    echo "  --dry-run               Print commands without executing"
    echo "  -h, --help              Show this help"
    echo ""
    echo "Example:"
    echo "  $0 -n blog-assistant -d 'AI-powered blog writing assistant'"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                TOOL_NAME="$2"
                shift 2
                ;;
            -d|--description)
                DESCRIPTION="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                help
                exit 1
                ;;
        esac
    done
}

validate_args() {
    if [[ -z "$TOOL_NAME" ]]; then
        echo "Error: Tool name is required"
        help
        exit 1
    fi

    TOOL_DIR="$HOME/.openclaw/workspace/tools/$TOOL_NAME"
    if [[ ! -d "$TOOL_DIR" ]]; then
        echo "Error: Tool directory not found: $TOOL_DIR"
        exit 1
    fi
}

create_readme() {
    local readme="$TOOL_DIR/README.md"
    if [[ -f "$readme" ]]; then
        echo "✅ README.md already exists"
        return
    fi

    cat > "$readme" << EOF
# $TOOL_NAME

${DESCRIPTION:-OpenSeneca tool for squad operations.}

## Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/$GITHUB_ORG/$TOOL_NAME.git
cd $TOOL_NAME

# Install dependencies
pip install -r requirements.txt  # or npm install for Node.js tools
\`\`\`

## Usage

\`\`\`bash
# Run the tool
python3 main.py  # or node main.js for Node.js tools
\`\`\`

## Development

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.
EOF

    echo "✅ Created README.md"
}

init_git_repo() {
    if [[ -d "$TOOL_DIR/.git" ]]; then
        echo "✅ Git repository already initialized"
        return
    fi

    local cmd="cd $TOOL_DIR && git init"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY RUN] $cmd"
    else
        eval "$cmd"
    fi

    echo "✅ Initialized git repository"
}

create_github_repo() {
    if ! command -v gh &> /dev/null; then
        echo "⚠️  GitHub CLI (gh) not found. Please install: https://cli.github.com/"
        return
    fi

    local cmd="gh repo create $GITHUB_ORG/$TOOL_NAME --public --source=$TOOL_DIR --remote=origin --push"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY RUN] $cmd"
    else
        eval "$cmd"
    fi

    echo "✅ Created GitHub repository: $GITHUB_ORG/$TOOL_NAME"
}

tag_release() {
    local cmd="cd $TOOL_DIR && git tag -a v$VERSION -m 'Release v$VERSION' && git push origin v$VERSION"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY RUN] $cmd"
    else
        eval "$cmd"
    fi

    echo "✅ Tagged release v$VERSION"
}

main() {
    parse_args "$@"
    validate_args

    echo "📦 Publishing tool: $TOOL_NAME"
    echo "   Version: $VERSION"
    if [[ -n "$DESCRIPTION" ]]; then
        echo "   Description: $DESCRIPTION"
    fi
    echo ""

    create_readme
    init_git_repo
    create_github_repo
    tag_release

    echo ""
    echo "✅ Tool published successfully!"
    echo "🔗 Repository: https://github.com/$GITHUB_ORG/$TOOL_NAME"
}

main "$@"
