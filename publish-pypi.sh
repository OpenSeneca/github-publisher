#!/usr/bin/env bash
# PyPI Publisher for OpenSeneca Tools
# Builds and publishes Python tools to PyPI

set -e

TOOL_NAME=""
VERSION=""
PYPI_TOKEN=""
GITHUB_ORG="OpenSeneca"
TOOLS_DIR="$HOME/.openclaw/workspace/tools"
SKIP_BUILD=false
TEST_PYPI=false

help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -n, --name NAME          Tool name (required)"
    echo "  -t, --token TOKEN        PyPI API token (or set TWINE_PASSWORD env var)"
    echo "  -v, --version VERSION    Version tag (default: reads from setup.py/pyproject.toml)"
    echo "  --skip-build             Skip build step, just upload existing dist/"
    echo "  --test-pypi              Publish to TestPyPI instead of PyPI"
    echo "  -h, --help               Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 -n squad-content-pipeline"
    echo "  $0 -n blog-assistant --test-pypi"
    echo "  TWINE_PASSWORD=pypi-xxx $0 -n squad-config-validator"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                TOOL_NAME="$2"
                shift 2
                ;;
            -t|--token)
                PYPI_TOKEN="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --test-pypi)
                TEST_PYPI=true
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

    TOOL_DIR="$TOOLS_DIR/$TOOL_NAME"
    if [[ ! -d "$TOOL_DIR" ]]; then
        echo "Error: Tool directory not found: $TOOL_DIR"
        exit 1
    fi

    # Check for setup.py or pyproject.toml
    if [[ ! -f "$TOOL_DIR/setup.py" ]] && [[ ! -f "$TOOL_DIR/pyproject.toml" ]]; then
        echo "Error: No setup.py or pyproject.toml found in $TOOL_DIR"
        exit 1
    fi
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 not found"
        exit 1
    fi

    if ! command -v twine &> /dev/null; then
        echo "Installing twine..."
        pip install --user --quiet twine
    fi

    if ! python3 -c "import build" 2>/dev/null; then
        echo "Installing build..."
        pip install --user --quiet build
    fi
}

get_version() {
    local tool_dir="$1"
    local version=""

    # Try to read from pyproject.toml
    if [[ -f "$tool_dir/pyproject.toml" ]]; then
        version=$(grep -E "^version\s*=" "$tool_dir/pyproject.toml" | head -1 | sed 's/.*=.*"\(.*\)".*/\1/' | tr -d '"'"'"')
    fi

    # Try to read from setup.py if not found
    if [[ -z "$version" ]] && [[ -f "$tool_dir/setup.py" ]]; then
        version=$(grep -E "version\s*=" "$tool_dir/setup.py" | head -1 | sed 's/.*=.*"\(.*\)".*/\1/' | tr -d '"'"'"')
    fi

    echo "$version"
}

clean_dist() {
    local tool_dir="$1"
    echo "Cleaning dist/ directory..."
    rm -rf "$tool_dir/dist"
    rm -rf "$tool_dir/build"
    rm -rf "$tool_dir"/*.egg-info
    echo "✅ Cleaned build artifacts"
}

build_package() {
    local tool_dir="$1"
    echo "Building package..."
    python3 -m build "$tool_dir" --outdir "$tool_dir/dist"
    echo "✅ Built package:"
    ls -lh "$tool_dir/dist"
}

upload_to_pypi() {
    local tool_dir="$1"
    local token="$2"
    local repository_url=""

    if [[ "$TEST_PYPI" == true ]]; then
        repository_url="--repository testpypi"
        echo "Publishing to TestPyPI..."
    else
        echo "Publishing to PyPI..."
    fi

    if [[ -z "$token" ]]; then
        token="${TWINE_PASSWORD:-}"
        if [[ -z "$token" ]]; then
            echo "Error: PyPI token not provided. Use -t or set TWINE_PASSWORD env var"
            exit 1
        fi
    fi

    TWINE_USERNAME="__token__" \
    TWINE_PASSWORD="$token" \
    twine upload "$tool_dir/dist/" \
        --skip-existing \
        $repository_url \
        --verbose

    echo "✅ Published to PyPI!"
}

verify_package() {
    local tool_name="$1"
    local version="$2"

    if [[ "$TEST_PYPI" == true ]]; then
        echo "Package URL: https://test.pypi.org/project/$tool_name/"
    else
        echo "Package URL: https://pypi.org/project/$tool_name/"
    fi

    echo ""
    echo "Install with:"
    if [[ "$TEST_PYPI" == true ]]; then
        echo "  pip install --index-url https://test.pypi.org/simple/ $tool_name"
    else
        echo "  pip install $tool_name"
    fi
}

main() {
    parse_args "$@"
    validate_args

    echo "📦 PyPI Publisher for OpenSeneca Tools"
    echo "   Tool: $TOOL_NAME"
    echo "   Repository: $TOOL_DIR"
    echo ""

    check_dependencies

    # Get version if not provided
    if [[ -z "$VERSION" ]]; then
        VERSION=$(get_version "$TOOL_DIR")
        if [[ -z "$VERSION" ]]; then
            echo "Error: Could not determine version. Please specify with -v"
            exit 1
        fi
    fi

    echo "   Version: $VERSION"
    echo ""

    # Clean and build
    clean_dist "$TOOL_DIR"

    if [[ "$SKIP_BUILD" == false ]]; then
        build_package "$TOOL_DIR"
    else
        echo "Skipping build step..."
        if [[ ! -d "$TOOL_DIR/dist" ]] || [[ -z "$(ls -A $TOOL_DIR/dist 2>/dev/null)" ]]; then
            echo "Error: dist/ is empty or doesn't exist. Cannot skip build."
            exit 1
        fi
    fi

    # Upload to PyPI
    upload_to_pypi "$TOOL_DIR" "$PYPI_TOKEN"

    # Show verification info
    verify_package "$TOOL_NAME" "$VERSION"

    echo ""
    echo "✅ Done!"
}

main "$@"
