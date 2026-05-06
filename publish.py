#!/usr/bin/env python3
"""
GitHub Publisher for OpenSeneca Tools
Python wrapper for publishing tools to GitHub organization
"""

import argparse
import subprocess
import sys
from pathlib import Path
import re

GITHUB_ORG = "OpenSeneca"
TOOLS_DIR = Path.home() / ".openclaw" / "workspace" / "tools"


def run_command(cmd, check=True, capture=False):
    """Run a shell command safely."""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, check=check, capture_output=True, text=True
            )
            return result.stdout.strip(), result.returncode
        else:
            subprocess.run(cmd, shell=True, check=check)
            return "", 0
    except subprocess.CalledProcessError as e:
        if check:
            print(f"❌ Command failed: {cmd}")
            print(f"   Error: {e}")
            sys.exit(1)
        return "", e.returncode


def tool_exists_in_github(tool_name):
    """Check if tool already exists in GitHub organization."""
    stdout, returncode = run_command(
        f"gh repo view {GITHUB_ORG}/{tool_name} 2>&1", check=False, capture=True
    )
    return returncode == 0


def validate_tool(tool_name):
    """Validate tool directory exists."""
    tool_dir = TOOLS_DIR / tool_name
    if not tool_dir.exists():
        print(f"❌ Tool directory not found: {tool_dir}")
        sys.exit(1)
    print(f"✅ Found tool directory: {tool_dir}")
    return tool_dir


def create_readme(tool_dir, tool_name, description, version):
    """Create or update README.md."""
    readme_path = tool_dir / "README.md"
    
    if readme_path.exists():
        print(f"✅ README.md already exists")
        return
    
    readme_content = f"""# {tool_name}

{description or "OpenSeneca tool for squad operations."}

## Installation

```bash
# Clone the repository
git clone https://github.com/{GITHUB_ORG}/{tool_name}.git
cd {tool_name}

# Install dependencies
pip install -r requirements.txt  # or npm install for Node.js tools
```

## Usage

```bash
# Run the tool
python3 main.py  # or node main.js for Node.js tools
```

## Development

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.
"""
    
    readme_path.write_text(readme_content)
    print(f"✅ Created README.md")


def init_git_repo(tool_dir):
    """Initialize git repository if not already done."""
    if (tool_dir / ".git").exists():
        print(f"✅ Git repository already initialized")
        return
    
    run_command(f"cd {tool_dir} && git init")
    print(f"✅ Initialized git repository")


def create_github_repo(tool_name, tool_dir, dry_run):
    """Create GitHub repository via GitHub CLI."""
    if tool_exists_in_github(tool_name):
        print(f"⚠️  Repository {GITHUB_ORG}/{tool_name} already exists")
        print("   Skipping repository creation, will just push existing code")
        return
    
    cmd = f"gh repo create {GITHUB_ORG}/{tool_name} --public --source={tool_dir} --remote=origin --push"
    
    if dry_run:
        print(f"[DRY RUN] {cmd}")
    else:
        run_command(cmd)
    
    print(f"✅ Created GitHub repository: {GITHUB_ORG}/{tool_name}")


def tag_release(tool_dir, version, dry_run):
    """Create and push version tag."""
    # Check if tag already exists
    stdout, returncode = run_command(
        f"cd {tool_dir} && git tag -l v{version}", capture=True, check=False
    )
    
    if stdout.strip() == f"v{version}":
        print(f"⚠️  Tag v{version} already exists")
        return
    
    cmd = f"cd {tool_dir} && git tag -a v{version} -m 'Release v{version}' && git push origin v{version}"
    
    if dry_run:
        print(f"[DRY RUN] {cmd}")
    else:
        run_command(cmd)
    
    print(f"✅ Tagged release v{version}")


def publish_tool(tool_name, description, version, dry_run):
    """Main function to publish a tool."""
    print(f"📦 Publishing tool: {tool_name}")
    print(f"   Version: {version}")
    if description:
        print(f"   Description: {description}")
    print()
    
    # Validate
    tool_dir = validate_tool(tool_name)
    
    # Create README
    create_readme(tool_dir, tool_name, description, version)
    
    # Initialize git
    init_git_repo(tool_dir)
    
    # Create GitHub repo
    create_github_repo(tool_name, tool_dir, dry_run)
    
    # Tag release
    tag_release(tool_dir, version, dry_run)
    
    print()
    print("✅ Tool published successfully!")
    print(f"🔗 Repository: https://github.com/{GITHUB_ORG}/{tool_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Publish OpenSeneca tools to GitHub organization"
    )
    parser.add_argument(
        "-n", "--name",
        required=True,
        help="Tool name (required)"
    )
    parser.add_argument(
        "-d", "--description",
        help="Tool description"
    )
    parser.add_argument(
        "-v", "--version",
        default="1.0.0",
        help="Version (default: 1.0.0)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing"
    )
    
    args = parser.parse_args()
    
    publish_tool(
        tool_name=args.name,
        description=args.description,
        version=args.version,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
