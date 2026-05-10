# GitHub Publisher

Package and publish OpenSeneca tools to PyPI and GitHub.

## What It Does

The GitHub Publisher automates the release process for OpenSeneca tools:

1. **Validates** the tool has proper packaging structure (setup.py, README.md, etc.)
2. **Builds** Python distributions (wheel + sdist)
3. **Publishes** to PyPI using twine
4. **Pushes** to GitHub repository
5. **Creates** GitHub release with version tag

## Usage

### GitHub Publishing

```bash
# Publish a tool to GitHub (create repo, push code, tag release)
python3 github_publisher.py -n squad-content-pipeline -d "Content Pipeline CLI for Seneca" -v 1.0.0

# Or use the bash wrapper
./publish-tool.sh -n squad-content-pipeline -d "Content Pipeline CLI for Seneca" -v 1.0.0

# Publish all tools with a version tag
./release-all-tools.sh 1.0.0
```

### PyPI Publishing

```bash
# Publish a Python package to PyPI
./publish-pypi.sh -n squad-content-pipeline

# Use PyPI token directly
./publish-pypi.sh -n squad-content-pipeline -t pypi-xxx

# Or use environment variable
TWINE_PASSWORD=pypi-xxx ./publish-pypi.sh -n squad-content-pipeline

# Test on TestPyPI first
./publish-pypi.sh -n squad-content-pipeline --test-pypi

# Skip build (use existing dist/)
./publish-pypi.sh -n squad-content-pipeline --skip-build
```

## Requirements

### Tool Requirements
The tool being published must have:
- `setup.py` or `pyproject.toml` with package metadata
- `README.md` with usage instructions
- Git repository with remote origin

### System Requirements
- Python 3.8+
- `build` package: `pip install build`
- `twine` package: `pip install twine`
- `gh` CLI (optional, for GitHub releases)
- PyPI credentials (in `~/.pypirc` or environment variables)

## Setup

### PyPI Credentials

Option 1: Using `~/.pypirc`
```bash
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-<your-token>
EOF
```

Option 2: Using environment variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-token>
```

### Install Dependencies
```bash
pip install build twine gh  # gh is optional
```

## Example Workflow

### Publishing to GitHub

1. **Prepare your tool** for publishing:
   - Ensure `README.md` exists
   - Commit all changes to git

2. **Run the GitHub publisher**:
   ```bash
   cd ~/.openclaw/workspace/tools/github-publisher
   ./publish-tool.sh -n your-tool-name -d "Description" -v 1.0.0
   ```

3. **Verify** on GitHub: `https://github.com/OpenSeneca/your-tool-name`

### Publishing to PyPI

1. **Ensure your tool has proper Python packaging**:
   - `setup.py` or `pyproject.toml` with version metadata
   - `LICENSE` file
   - `README.md`

2. **Build and publish**:
   ```bash
   cd ~/.openclaw/workspace/tools/github-publisher
   TWINE_PASSWORD=pypi-xxx ./publish-pypi.sh -n your-tool-name
   ```

3. **Verify** on PyPI: `https://pypi.org/project/your-tool-name/`

4. **Install**:
   ```bash
   pip install your-tool-name
   ```

## Error Handling

The GitHub publisher will stop on critical errors but continue on non-critical ones:

- **Critical** (stops execution):
  - Tool directory not found
  - Missing `setup.py` or `README.md`
  - Git push failure

- **Non-critical** (warns and continues):
  - GitHub release creation failure
  - Uncommitted changes (auto-commits)

The PyPI publisher will stop on:
- Missing `setup.py` or `pyproject.toml`
- Build failures
- Authentication errors with PyPI token

## Current Projects

### GitHub Published
- ✅ `content-pipeline` - Content Pipeline CLI for Seneca
- ✅ `axon-ingester` - Auto-Ingester for Axon
- ✅ `blog-assistant` - Blog Draft Assistant
- ✅ `squad-config-validator` - Config Validator
- ✅ `squad-activity-digest` - Squad Activity Digest
- ✅ `auto-ingester-axon` - Axon Auto-Ingester
- ✅ `github-publisher` - This tool
- ✅ `competitor-tracker` - Competitor Tracker
- ✅ `blog-publisher` - Blog Publisher

### Pending PyPI Publication
Use `publish-pypi.sh` to publish these to PyPI:
- ⏳ `squad-deployer` - Deployment automation
- ⏳ `squad-ssh-manager` - SSH key management

## Deployment

Local use only. No cron job needed - run manually when ready to publish.

---

*Created by Archimedes (Engineering) on 2026-05-08*
