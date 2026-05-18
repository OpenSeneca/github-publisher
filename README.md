# GitHub Publisher v1.1.0

Automates building and publishing squad tools to GitHub releases, PyPI, and OpenSeneca organization.

## Features

- **Tool discovery**: Automatically finds all Python packages in the tools directory
- **Batch operations**: Build, publish, or release all tools at once
- **Selective processing**: Target specific tools by name
- **GitHub integration**: Creates GitHub releases with auto-generated notes
- **PyPI publishing**: Uploads packages to PyPI with token or .pypirc authentication
- **Metadata extraction**: Reads version and description from setup.py/pyproject.toml
- **Git status checking**: Shows uncommitted changes when listing tools
- **Ready-to-publish checks**: Validates tools have version, README, and LICENSE before publishing
- **Org sync**: Sync tools to OpenSeneca GitHub organization
- **Packaging**: Create portable packages for distribution

## Installation

```bash
pip install -e .
```

## Usage

### List all discoverable tools

```bash
github-publisher list
```

List only tools ready to publish:
```bash
github-publisher list --ready-only
```

With verbose output:
```bash
github-publisher list --verbose
```

### Build all tools

```bash
github-publisher build
```

Build specific tools:
```bash
github-publisher build content-pipeline paper-summarizer
```

### Publish all tools to PyPI

```bash
github-publisher publish
```

With PyPI token:
```bash
github-publisher publish --token pypi-xxx
```

### Create GitHub releases for all tools

```bash
github-publisher release
```

### Sync tools to OpenSeneca organization

```bash
github-publisher sync
```

Sync specific tools:
```bash
github-publisher sync content-pipeline squad-disk-monitor
```

### Package tools for distribution

```bash
github-publisher package
```

Package specific tools:
```bash
github-publisher package --output-dir /tmp/packages content-pipeline
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all discoverable tools with metadata |
| `build` | Build distribution packages for tools |
| `publish` | Publish packages to PyPI |
| `release` | Create GitHub releases from tags |
| `sync` | Sync tools to OpenSeneca GitHub organization |
| `package` | Create portable packages for distribution |

## How It Works

### Tool Discovery

The publisher scans `~/.openclaw/workspace/tools/` for directories containing:
- `setup.py` OR `pyproject.toml`
- Not in ignored list (archive, node_modules, __pycache__)

### Ready-to-Publish Checks

A tool is considered ready to publish when it has:
- Version defined in setup.py or pyproject.toml
- Git repository initialized
- README.md file
- LICENSE file

Only tools that pass these checks are synced to the organization or included in package output.

### Building

For each tool:
1. Cleans previous builds (dist/, build/, *.egg-info)
2. Runs `python -m build` to create wheel and source distribution
3. Verifies build artifacts exist

### Publishing to PyPI

1. Builds the package (if needed)
2. Uses `twine upload` to publish
3. Supports either PyPI token or `.pypirc` configuration
4. Uploads both wheel and source distribution

### GitHub Releases

1. Creates annotated git tag: `v<version>`
2. Pushes tag to origin
3. Creates GitHub release using `gh release create`
4. Auto-generates release notes

### Org Sync

1. Checks if repository exists in OpenSeneca organization
2. Creates repository if it doesn't exist
3. Sets up remote `origin` to point to org repository
4. Pushes to GitHub (main or master branch)

Only tools that pass ready-to-publish checks are synced.

### Packaging

1. Creates a portable tar.gz package for each tool
2. Includes: main.py, setup.py, pyproject.toml, README.md, LICENSE, install.sh
3. Packages are saved to `_packages/` directory by default

## Requirements

- Python 3.8+
- `build` package (for building wheels)
- `twine` package (for PyPI publishing)
- `gh` CLI (for GitHub releases)
- Git (for tagging)

## Configuration

### PyPI Token

Option 1: Use `.pypirc` file:
```ini
[pypi]
username = __token__
password = pypi-...
```

Option 2: Pass token via CLI:
```bash
github-publisher publish --token pypi-xxx
```

### GitHub CLI

Install from https://cli.github.com/ and authenticate:
```bash
gh auth login
```

## Examples

### Build and publish a specific tool

```bash
github-publisher build content-pipeline
github-publisher publish --token pypi-xxx content-pipeline
```

### Create a GitHub release after publishing

```bash
github-publisher release content-pipeline
```

### Workflow for new tool

1. Make sure tool has version in setup.py or pyproject.toml
2. Commit and push changes
3. Build: `github-publisher build my-tool`
4. Publish: `github-publisher publish --token pypi-xxx my-tool`
5. Release: `github-publisher release my-tool`

## Error Handling

- Missing `build` or `twine` dependencies
- Invalid PyPI token
- No GitHub CLI installed or not authenticated
- Git not initialized in tool directory
- Version not found in package metadata

## Development

```bash
# Install in development mode
pip install -e .

# Run with verbose logging
github-publisher list --verbose
```

## License

MIT
