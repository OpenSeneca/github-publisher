# GitHub Publisher

CLI tool for publishing OpenSeneca tools to PyPI and setting up GitHub repositories.

**v1.1.0** - Dynamically discovers all tools, batch build/publish modes

## Installation

```bash
cd ~/.openclaw/workspace/tools/github-publisher
pip install -e .
```

Or install from GitHub:
```bash
pip install git+https://github.com/OpenSeneca/github-publisher.git
```

## Usage

### List all available tools

```bash
github-publisher --list-tools
# or
python3 main.py --list-tools
```

This dynamically discovers all Python packages in the tools directory (requires setup.py or pyproject.toml).

### Set up GitHub repository for a tool

```bash
github-publisher --tool squad-deployer --setup-github
```

This will:
- Initialize git repository if needed
- Add GitHub remote (https://github.com/OpenSeneca/{tool}.git)
- Print instructions for creating the repository on GitHub

### Build distribution packages

```bash
github-publisher --tool squad-deployer --build
```

This builds both wheel and source distribution.

### Build ALL tools (batch mode)

```bash
# Build all tools, skip already built ones
github-publisher --build-all

# Rebuild everything even if dist files exist
github-publisher --build-all --rebuild
```

### Publish to PyPI

```bash
github-publisher --tool squad-deployer --publish
```

For testing, publish to Test PyPI first:

```bash
github-publisher --tool squad-deployer --publish --test-pypi
```

### Publish ALL tools (batch mode)

```bash
# Publish all built tools to production PyPI
github-publisher --publish-all

# Publish all to Test PyPI
github-publisher --publish-all --test-pypi
```

### Complete workflow (single tool)

```bash
# 1. Setup GitHub repository
github-publisher --tool squad-deployer --setup-github

# 2. Build packages
github-publisher --tool squad-deployer --build

# 3. Publish to Test PyPI (for testing)
github-publisher --tool squad-deployer --publish --test-pypi

# 4. Publish to production PyPI
github-publisher --tool squad-deployer --publish
```

### Complete workflow (batch mode)

```bash
# Build all tools
github-publisher --build-all

# Publish all to Test PyPI
github-publisher --publish-all --test-pypi

# Publish all to production PyPI
github-publisher --publish-all
```

## Prerequisites

### For publishing to PyPI:

1. Install required packages:
   ```bash
   pip install build twine
   ```

2. Configure PyPI authentication (one-time setup):

   Option A: Using API token (recommended):
   ```bash
   # Create ~/.pypirc
   cat > ~/.pypirc << 'EOF'
   [pypi]
   username = __token__
   password = <your-pypi-token>

   [testpypi]
   username = __token__
   password = <your-testpypi-token>
   EOF
   chmod 600 ~/.pypirc
   ```

   Option B: Using keyring (more secure):
   ```bash
   pip install keyring
   keyring set https://upload.pypi.org/legacy/ __token__
   # Enter your PyPI API token when prompted
   ```

### For GitHub:

1. Create a GitHub personal access token with `repo` scope
2. Configure git credentials:
   ```bash
   git config --global credential.helper store
   git config --global user.name "OpenSeneca Squad"
   git config --global user.email "squad@openseneca.org"
   ```

## Features

- ✅ **Dynamic tool discovery** - Automatically finds all Python packages in tools directory
- ✅ **Batch operations** - Build and publish all tools at once
- ✅ List all OpenSeneca tools with their status
- ✅ Set up GitHub repositories (git init, remote add)
- ✅ Build distribution packages (wheel + sdist)
- ✅ Publish to PyPI (production or test)
- ✅ Version detection from setup.py and pyproject.toml
- ✅ Status checking (setup.py, dist, git, remote)
- ✅ Skip already-built tools in batch mode
- ✅ Verbose logging for debugging

## Supported Tools

Tools are dynamically discovered from the tools directory. Run `github-publisher --list-tools` to see all available packages.

Any directory in `~/.openclaw/workspace/tools/` that contains a `setup.py` or `pyproject.toml` file will be automatically detected.

## Troubleshooting

### "No distribution packages found"
Run `--build` first to create the packages.

### "twine is not installed"
Install it with: `pip install twine build`

### "403 Forbidden" when publishing
Check that your PyPI token is valid and has correct permissions.

### "Repository not found" when pushing
Create the repository on GitHub first: https://github.com/new

## License

MIT License - see LICENSE file for details.

## Version

**v1.1.0** - 2026-05-15
- Added dynamic tool discovery (no more hardcoded lists)
- Added --build-all batch mode
- Added --publish-all batch mode
- Added --rebuild flag to force rebuilds
- Improved filtering (skips archived directories starting with _)
- Support for both setup.py and pyproject.toml

**v1.0.0** - Initial release
