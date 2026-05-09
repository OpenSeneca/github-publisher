#!/usr/bin/env python3
"""
GitHub Publisher for OpenSeneca Tools.

Publishes OpenSeneca tools to GitHub organizations:
- Initializes git repos for local tools
- Creates GitHub repositories via GitHub CLI
- Pushes code with proper remote configuration
- Supports README generation, .gitignore, LICENSE
- Can package tools for PyPI if setup.py/pyproject.toml exists
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace" / "tools"
GITHUB_ORG = "OpenSeneca"
DEFAULT_LICENSE = "MIT"
DEFAULT_BRANCH = "main"


def run_cmd(cmd, check=True, capture_output=False, cwd=None):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(
            cmd,
            shell=False,
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print(f"✗ Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
            print(f"  Error: {e.stderr}")
        raise


def init_git_repo(tool_path):
    """Initialize git repository if not already initialized"""
    git_dir = tool_path / ".git"
    if git_dir.exists():
        print(f"  ✓ Git repo already initialized")
        return True
    
    try:
        run_cmd(["git", "init"], cwd=tool_path)
        print(f"  ✓ Initialized git repo")
        return True
    except Exception as e:
        print(f"  ✗ Failed to initialize git: {e}")
        return False


def create_github_repo(tool_name, tool_path):
    """Create GitHub repository using GitHub CLI"""
    try:
        # Check if gh CLI is available
        run_cmd(["gh", "auth", "status"], check=True, capture_output=True)
    except:
        print(f"  ✗ GitHub CLI (gh) not found or not authenticated")
        return False
    
    repo_name = f"{GITHUB_ORG}/{tool_name}"
    
    try:
        # Check if repo already exists
        result = run_cmd(
            ["gh", "repo", "view", repo_name],
            check=False,
            capture_output=True
        )
        if result.returncode == 0:
            print(f"  ✓ GitHub repo already exists: {repo_name}")
            return True
        
        # Create new repo
        run_cmd([
            "gh", "repo", "create",
            repo_name,
            "--public",
            "--description", f"OpenSeneca tool: {tool_name}"
        ])
        
        print(f"  ✓ Created GitHub repo: {repo_name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to create GitHub repo: {e}")
        return False


def configure_remote(tool_path, tool_name):
    """Configure git remote to point to GitHub"""
    repo_url = f"git@github.com:{GITHUB_ORG}/{tool_name}.git"
    
    try:
        # Check if origin remote exists
        result = run_cmd(
            ["git", "remote", "get-url", "origin"],
            check=False,
            capture_output=True,
            cwd=tool_path
        )
        
        if result.returncode == 0:
            # Update existing remote
            run_cmd(["git", "remote", "set-url", "origin", repo_url], cwd=tool_path)
        else:
            # Add new remote
            run_cmd(["git", "remote", "add", "origin", repo_url], cwd=tool_path)
        
        print(f"  ✓ Configured remote: {repo_url}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to configure remote: {e}")
        return False


def initial_commit(tool_path, tool_name):
    """Create initial commit with all files"""
    try:
        run_cmd(["git", "add", "."], cwd=tool_path)
        run_cmd([
            "git", "commit",
            "-m", f"Initial commit: {tool_name}"
        ], cwd=tool_path)
        print(f"  ✓ Created initial commit")
        return True
    except Exception as e:
        # If nothing to commit, that's ok
        if "nothing to commit" in str(e):
            print(f"  ✓ Nothing to commit (repo up to date)")
            return True
        print(f"  ✗ Failed to create commit: {e}")
        return False


def push_to_github(tool_path):
    """Push code to GitHub"""
    try:
        # Get current branch name
        result = run_cmd(
            ["git", "branch", "--show-current"],
            check=True,
            capture_output=True,
            cwd=tool_path
        )
        branch = result.stdout.strip()
        
        if not branch:
            print(f"  ✗ Could not determine current branch")
            return False
        
        # Push current branch
        result = run_cmd(
            ["git", "push", "-u", "origin", branch],
            check=False,
            capture_output=True,
            cwd=tool_path
        )
        
        if result.returncode == 0:
            print(f"  ✓ Pushed to GitHub ({branch})")
            return True
        
        print(f"  ✗ Failed to push: {result.stderr}")
        return False
        
    except Exception as e:
        print(f"  ✗ Failed to push: {e}")
        return False


def ensure_readme(tool_path, tool_name):
    """Ensure README.md exists"""
    readme_path = tool_path / "README.md"
    
    if readme_path.exists():
        print(f"  ✓ README.md exists")
        return True
    
    try:
        readme_content = f"""# {tool_name}

OpenSeneca tool: {tool_name}

## Installation

```bash
# Clone from GitHub
git clone https://github.com/{GITHUB_ORG}/{tool_name}.git
cd {tool_name}
```

## Usage

See the tool's documentation for usage instructions.

## License

{DEFAULT_LICENSE}

## Status

**Published:** ✅ GitHub: https://github.com/{GITHUB_ORG}/{tool_name}
**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}
"""
        readme_path.write_text(readme_content)
        print(f"  ✓ Created README.md")
        return True
    except Exception as e:
        print(f"  ✗ Failed to create README: {e}")
        return False


def ensure_gitignore(tool_path):
    """Ensure .gitignore exists"""
    gitignore_path = tool_path / ".gitignore"
    
    if gitignore_path.exists():
        return True
    
    try:
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv/

# Package builds
dist/
build/
*.egg-info/
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
        gitignore_path.write_text(gitignore_content)
        return True
    except Exception:
        return False


def ensure_license(tool_path):
    """Ensure LICENSE file exists"""
    license_path = tool_path / "LICENSE"
    
    if license_path.exists():
        return True
    
    try:
        # Only create simple MIT license if requested
        # For now, skip to avoid complexity
        return True
    except Exception:
        return False


def package_for_pypi(tool_path):
    """Package tool for PyPI if setup.py or pyproject.toml exists"""
    setup_py = tool_path / "setup.py"
    pyproject_toml = tool_path / "pyproject.toml"
    
    if not (setup_py.exists() or pyproject_toml.exists()):
        print(f"  ℹ No setup.py/pyproject.toml - skipping PyPI packaging")
        return None
    
    try:
        # Clean previous builds
        dist_dir = tool_path / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # Build package
        run_cmd(["python", "-m", "build"], cwd=tool_path)
        print(f"  ✓ Built package for PyPI")
        
        # Check what was built
        built_files = list(dist_dir.glob("*"))
        if built_files:
            print(f"    Built: {[f.name for f in built_files]}")
            return built_files
        return None
        
    except Exception as e:
        print(f"  ⚠ Failed to build PyPI package: {e}")
        return None


def publish_tool(tool_path, tool_name, create_github=True, build_pypi=False):
    """Publish a tool to GitHub (and optionally PyPI)"""
    print(f"\n🚀 Publishing: {tool_name}")
    print(f"   Path: {tool_path}")
    
    success = True
    
    # Ensure essential files
    if not ensure_readme(tool_path, tool_name):
        success = False
    ensure_gitignore(tool_path)
    ensure_license(tool_path)
    
    # Initialize git repo
    if not init_git_repo(tool_path):
        success = False
    
    # Create GitHub repo
    if create_github:
        if not create_github_repo(tool_name, tool_path):
            success = False
        
        # Configure remote
        if not configure_remote(tool_path, tool_name):
            success = False
    
    # Commit changes
    if not initial_commit(tool_path, tool_name):
        success = False
    
    # Push to GitHub
    if create_github:
        if not push_to_github(tool_path):
            success = False
    
    # Package for PyPI if requested
    if build_pypi:
        package_for_pypi(tool_path)
    
    if success:
        print(f"  ✅ Published: {tool_name}")
        return True
    else:
        print(f"  ⚠ Published with errors: {tool_name}")
        return False


def discover_tools():
    """Discover all tools in workspace/tools/"""
    tools = []
    
    for item in WORKSPACE.iterdir():
        # Skip archived and hidden directories
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        
        if item.is_dir():
            # Skip if already a git repo with origin pointing to OpenSeneca
            git_dir = item / ".git"
            if git_dir.exists():
                try:
                    result = run_cmd(
                        ["git", "remote", "get-url", "origin"],
                        check=False,
                        capture_output=True,
                        cwd=item
                    )
                    if result.returncode == 0 and f"{GITHUB_ORG}/" in result.stdout:
                        print(f"  ℹ Skipping {item.name} (already published to {GITHUB_ORG})")
                        continue
                except:
                    pass
            
            tools.append((item.name, item))
    
    return tools


def main():
    """Main entry point"""
    print("=" * 60)
    print("GitHub Publisher for OpenSeneca Tools")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Publish specific tool
        tool_name = sys.argv[1]
        tool_path = WORKSPACE / tool_name
        
        if not tool_path.exists():
            print(f"✗ Tool not found: {tool_path}")
            sys.exit(1)
        
        create_github = "--no-github" not in sys.argv
        build_pypi = "--pypi" in sys.argv
        
        publish_tool(tool_path, tool_name, create_github=create_github, build_pypi=build_pypi)
    else:
        # Publish all unpublished tools
        tools = discover_tools()
        
        if not tools:
            print("No tools to publish")
            return
        
        print(f"\nFound {len(tools)} unpublished tool(s)")
        
        for tool_name, tool_path in tools:
            publish_tool(tool_path, tool_name)
        
        print("\n" + "=" * 60)
        print(f"Published {len(tools)} tool(s)")
        print("=" * 60)


if __name__ == "__main__":
    main()
