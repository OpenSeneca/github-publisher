#!/usr/bin/env python3
"""
GitHub Publisher v1.0.0
Automates building and publishing squad tools to GitHub and PyPI.
"""

import os
import sys
import json
import subprocess
import argparse
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TOOLS_DIR = WORKSPACE / "tools"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

# Tool patterns to ignore
IGNORED_TOOLS = {"archive", "node_modules", "__pycache__", "_archive-", ".git"}

# OpenSeneca GitHub org configuration
OPEN_SENECA_ORG = "OpenSeneca"


def run_command(cmd: List[str], cwd: Optional[Path] = None, capture: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def discover_tools(tools_dir: Path) -> List[Path]:
    """Discover all tool directories that contain package metadata."""
    tools = []

    for item in tools_dir.iterdir():
        if not item.is_dir():
            continue

        # Skip ignored tools
        if item.name in IGNORED_TOOLS or item.name.startswith("_archive-"):
            continue

        # Check if it's a Python package (has setup.py or pyproject.toml)
        if (item / "setup.py").exists() or (item / "pyproject.toml").exists():
            tools.append(item)

    return sorted(tools)


def get_tool_info(tool_path: Path) -> Dict:
    """Extract tool metadata from setup.py or pyproject.toml."""
    info = {
        "name": tool_path.name,
        "path": tool_path,
        "has_git": (tool_path / ".git").exists(),
        "version": None,
        "description": "",
        "has_setup": (tool_path / "setup.py").exists(),
        "has_pyproject": (tool_path / "pyproject.toml").exists(),
        "has_readme": (tool_path / "README.md").exists(),
        "has_license": (tool_path / "LICENSE").exists(),
        "ready_to_publish": False,
    }

    # Try to extract version from setup.py
    if info["has_setup"]:
        try:
            with open(tool_path / "setup.py", "r") as f:
                content = f.read()
                # Find version='...' or version="..."
                match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    info["version"] = match.group(1)
        except Exception:
            pass

    # Try pyproject.toml
    if info["has_pyproject"] and not info["version"]:
        try:
            with open(tool_path / "pyproject.toml", "r") as f:
                content = f.read()
                match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    info["version"] = match.group(1)
        except Exception:
            pass

    # Check if tool is ready to publish
    info["ready_to_publish"] = all([
        info["version"] is not None,
        info["has_git"],
        info["has_readme"],
        info["has_license"]
    ])

    return info


def build_tool(tool_path: Path, verbose: bool = False) -> bool:
    """Build a Python package for distribution."""
    print(f"Building {tool_path.name}...")

    # Clean previous builds
    build_dirs = ["dist", "build", "*.egg-info"]
    for pattern in build_dirs:
        for path in tool_path.glob(pattern):
            if path.is_dir():
                import shutil
                shutil.rmtree(path)

    # Build the package
    cmd = [sys.executable, "-m", "build"]
    returncode, stdout, stderr = run_command(cmd, cwd=tool_path)

    if verbose:
        print(stdout)
        if stderr:
            print(stderr)

    if returncode != 0:
        print(f"❌ Failed to build {tool_path.name}")
        return False

    # Check if build artifacts exist
    dist_dir = tool_path / "dist"
    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        print(f"❌ No build artifacts found for {tool_path.name}")
        return False

    print(f"✅ Built {tool_path.name}")
    return True


def publish_to_pypi(tool_path: Path, token: Optional[str] = None, verbose: bool = False) -> bool:
    """Publish a package to PyPI."""
    print(f"Publishing {tool_path.name} to PyPI...")

    # Check if twine is installed
    try:
        import twine
    except ImportError:
        print("❌ twine not installed. Install with: pip install twine")
        return False

    # Build the package first
    if not build_tool(tool_path, verbose):
        return False

    # Publish using twine
    dist_dir = tool_path / "dist"
    if token:
        # Use token from CLI
        cmd = ["twine", "upload", f"--username=__token__", f"--password={token}", f"{dist_dir}/*"]
    else:
        # Use .pypirc configuration
        cmd = ["twine", "upload", f"{dist_dir}/*"]

    returncode, stdout, stderr = run_command(cmd, cwd=tool_path)

    if verbose:
        print(stdout)
        if stderr:
            print(stderr)

    if returncode != 0:
        print(f"❌ Failed to publish {tool_path.name} to PyPI")
        return False

    print(f"✅ Published {tool_path.name} to PyPI")
    return True


def create_github_release(tool_path: Path, tag: str, verbose: bool = False) -> bool:
    """Create a GitHub release for a tool."""
    print(f"Creating GitHub release for {tool_path.name} (tag: {tag})...")

    # Check if gh CLI is available
    returncode, _, _ = run_command(["gh", "--version"])
    if returncode != 0:
        print("❌ gh CLI not found. Install from: https://cli.github.com/")
        return False

    # Create and push tag
    cmd = ["git", "tag", "-a", tag, "-m", f"Release {tag}"]
    returncode, stdout, stderr = run_command(cmd, cwd=tool_path)

    if returncode != 0:
        print(f"❌ Failed to create tag: {stderr}")
        return False

    # Push tag
    cmd = ["git", "push", "origin", tag]
    returncode, stdout, stderr = run_command(cmd, cwd=tool_path)

    if returncode != 0:
        print(f"❌ Failed to push tag: {stderr}")
        return False

    # Create GitHub release
    cmd = ["gh", "release", "create", tag, "--generate-notes"]
    returncode, stdout, stderr = run_command(cmd, cwd=tool_path)

    if verbose:
        print(stdout)
        if stderr:
            print(stderr)

    if returncode != 0:
        print(f"❌ Failed to create GitHub release: {stderr}")
        return False

    print(f"✅ Created GitHub release {tag} for {tool_path.name}")
    return True


def list_tools(verbose: bool = False, ready_only: bool = False):
    """List all discoverable tools with their metadata."""
    tools = discover_tools(TOOLS_DIR)

    if not tools:
        print("No tools found.")
        return

    if ready_only:
        tools = [t for t in tools if get_tool_info(t)["ready_to_publish"]]
        if not tools:
            print("No tools ready to publish.")
            return

    print(f"\nFound {len(tools)} tools:\n")

    for tool_path in tools:
        info = get_tool_info(tool_path)
        status_icon = "✅" if info["ready_to_publish"] else "⚠️ "
        print(f"{status_icon} {info['name']}")
        print(f"   Version: {info['version'] or 'Unknown'}")
        print(f"   Path: {info['path']}")
        print(f"   Git: {'✅' if info['has_git'] else '❌'}")
        print(f"   README: {'✅' if info['has_readme'] else '❌'}")
        print(f"   LICENSE: {'✅' if info['has_license'] else '❌'}")
        print(f"   Setup: {'setup.py' if info['has_setup'] else 'pyproject.toml' if info['has_pyproject'] else 'none'}")

        if verbose and info['has_git']:
            # Get git status
            returncode, stdout, stderr = run_command(["git", "status", "--short"], cwd=tool_path)
            if stdout.strip():
                print(f"   Git status: {stdout.strip()}")

        print()


def build_all(tools: Optional[List[str]] = None, verbose: bool = False):
    """Build all tools or specific tools."""
    all_tools = discover_tools(TOOLS_DIR)

    if tools:
        # Filter by tool names
        all_tools = [t for t in all_tools if t.name in tools]
        if not all_tools:
            print(f"❌ No matching tools found: {tools}")
            return

    success_count = 0
    for tool_path in all_tools:
        if build_tool(tool_path, verbose):
            success_count += 1

    print(f"\n✅ Built {success_count}/{len(all_tools)} tools")


def publish_all(tools: Optional[List[str]] = None, token: Optional[str] = None, verbose: bool = False):
    """Publish all tools or specific tools to PyPI."""
    all_tools = discover_tools(TOOLS_DIR)

    if tools:
        # Filter by tool names
        all_tools = [t for t in all_tools if t.name in tools]
        if not all_tools:
            print(f"❌ No matching tools found: {tools}")
            return

    if not token:
        print("⚠️  No PyPI token provided. Will attempt to use .pypirc configuration.")
        response = input("Continue? [y/N] ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    success_count = 0
    for tool_path in all_tools:
        if publish_to_pypi(tool_path, token, verbose):
            success_count += 1

    print(f"\n✅ Published {success_count}/{len(all_tools)} tools to PyPI")


def release_all(tools: Optional[List[str]] = None, verbose: bool = False):
    """Create GitHub releases for all tools or specific tools."""
    all_tools = discover_tools(TOOLS_DIR)

    if tools:
        # Filter by tool names
        all_tools = [t for t in all_tools if t.name in tools]
        if not all_tools:
            print(f"❌ No matching tools found: {tools}")
            return

    success_count = 0
    for tool_path in all_tools:
        info = get_tool_info(tool_path)

        if not info['version']:
            print(f"⚠️  Skipping {tool_path.name}: No version found")
            continue

        tag = f"v{info['version']}"
        if create_github_release(tool_path, tag, verbose):
            success_count += 1

    print(f"\n✅ Created {success_count}/{len(all_tools)} GitHub releases")


def sync_to_github_org(tools: Optional[List[str]] = None, org: str = OPEN_SENECA_ORG, verbose: bool = False):
    """Sync tools to OpenSeneca GitHub org."""
    all_tools = discover_tools(TOOLS_DIR)

    if tools:
        # Filter by tool names
        all_tools = [t for t in all_tools if t.name in tools]
        if not all_tools:
            print(f"❌ No matching tools found: {tools}")
            return

    # Check if gh CLI is available
    returncode, _, _ = run_command(["gh", "--version"])
    if returncode != 0:
        print("❌ gh CLI not found. Install from: https://cli.github.com/")
        return

    success_count = 0
    for tool_path in all_tools:
        info = get_tool_info(tool_path)
        repo_name = info['name']
        
        print(f"\n🔄 Syncing {repo_name} to {org}/{repo_name}...")
        
        # Check if tool is ready
        if not info['ready_to_publish']:
            print(f"⚠️  Skipping {repo_name}: Not ready (missing version, README, or LICENSE)")
            continue
        
        # Check if repo already exists in the org
        returncode, stdout, stderr = run_command(
            ["gh", "repo", "view", f"{org}/{repo_name}"],
            capture=False
        )
        
        if returncode == 0:
            print(f"✓ Repository {org}/{repo_name} already exists")
            
            # Check if it's the same remote
            returncode, stdout, stderr = run_command(
                ["git", "remote", "-v"],
                cwd=tool_path
            )
            
            if f"git@github.com:{org}/{repo_name}" not in stdout and f"https://github.com/{org}/{repo_name}" not in stdout:
                print(f"⚠️  Tool has different remote. Current remotes:")
                print(stdout.strip())
                
                # Ask to add org remote
                # For automation, skip interactive prompts
                if not verbose:
                    print(f"⚠️  Skipping {repo_name}: Different remote (use --verbose for details)")
                    continue
        else:
            # Create new repo in the org
            print(f"Creating repository {org}/{repo_name}...")
            
            returncode, stdout, stderr = run_command(
                ["gh", "repo", "create", f"{org}/{repo_name}", "--public", "--description", info['description'] or f"{repo_name} tool"],
                capture=False
            )
            
            if returncode != 0:
                print(f"❌ Failed to create repo: {stderr}")
                continue
        
        # Add remote if not already added
        returncode, stdout, stderr = run_command(
            ["git", "remote", "get-url", "origin"],
            cwd=tool_path
        )
        
        if returncode != 0:
            # Add origin remote
            remote_url = f"git@github.com:{org}/{repo_name}.git"
            returncode, stdout, stderr = run_command(
                ["git", "remote", "add", "origin", remote_url],
                cwd=tool_path
            )
            if returncode != 0:
                print(f"❌ Failed to add remote: {stderr}")
                continue
        
        # Push to GitHub
        print(f"Pushing {repo_name} to {org}/{repo_name}...")
        returncode, stdout, stderr = run_command(
            ["git", "push", "-u", "origin", "main"],
            cwd=tool_path,
            capture=False
        )
        
        if returncode != 0:
            # Try master branch
            returncode, stdout, stderr = run_command(
                ["git", "push", "-u", "origin", "master"],
                cwd=tool_path,
                capture=False
            )
            
            if returncode != 0:
                print(f"❌ Failed to push to GitHub: {stderr}")
                continue
        
        print(f"✅ Synced {repo_name} to {org}/{repo_name}")
        success_count += 1
    
    print(f"\n✅ Synced {success_count}/{len(all_tools)} tools to {org}")


def package_for_org(tools: Optional[List[str]] = None, output_dir: Optional[Path] = None, verbose: bool = False):
    """Package tools for OpenSeneca org deployment."""
    all_tools = discover_tools(TOOLS_DIR)

    if tools:
        # Filter by tool names
        all_tools = [t for t in all_tools if t.name in tools]
        if not all_tools:
            print(f"❌ No matching tools found: {tools}")
            return

    # Default output directory
    if output_dir is None:
        output_dir = TOOLS_DIR / "_packages"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for tool_path in all_tools:
        info = get_tool_info(tool_path)
        
        if not info['ready_to_publish']:
            if verbose:
                print(f"⚠️  Skipping {info['name']}: Not ready")
            continue
        
        # Create a portable package
        package_name = f"{info['name']}-{info['version']}"
        package_path = output_dir / f"{package_name}.tar.gz"
        
        print(f"Packaging {info['name']}...")
        
        # Create a temporary directory for the package
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / package_name
            tmp_path.mkdir()
            
            # Copy relevant files
            files_to_copy = ["main.py", "setup.py", "pyproject.toml", "README.md", "LICENSE"]
            for file_name in files_to_copy:
                src = tool_path / file_name
                if src.exists():
                    shutil.copy2(src, tmp_path / file_name)
            
            # Create a simple install script
            install_script = tmp_path / "install.sh"
            install_script.write_text(f"""#!/bin/bash
# Install {info['name']}
set -e

# Install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Install package
pip install .

echo "Installed {info['name']} v{info['version']}"
""")
            install_script.chmod(0o755)
            
            # Create tar.gz
            shutil.make_archive(str(package_path.with_suffix('')), 'gztar', str(tmp_path.parent), package_name)
        
        print(f"✅ Packaged {info['name']} to {package_path}")
        success_count += 1
    
    print(f"\n✅ Packaged {success_count}/{len(all_tools)} tools to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Publisher - Automate building and publishing squad tools"
    )
    parser.add_argument(
        "command",
        choices=["list", "build", "publish", "release", "sync", "package"],
        help="Command to run"
    )
    parser.add_argument(
        "tools",
        nargs="*",
        help="Specific tools to process (default: all tools)"
    )
    parser.add_argument(
        "--token",
        help="PyPI API token (for publish command)"
    )
    parser.add_argument(
        "--org",
        default=OPEN_SENECA_ORG,
        help=f"GitHub organization name (default: {OPEN_SENECA_ORG})"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for package command"
    )
    parser.add_argument(
        "--ready-only",
        action="store_true",
        help="Only process tools that are ready to publish"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="GitHub Publisher v1.1.0"
    )

    args = parser.parse_args()

    if args.command == "list":
        list_tools(args.verbose, args.ready_only)
    elif args.command == "build":
        build_all(args.tools, args.verbose)
    elif args.command == "publish":
        publish_all(args.tools, args.token, args.verbose)
    elif args.command == "release":
        release_all(args.tools, args.verbose)
    elif args.command == "sync":
        sync_to_github_org(args.tools, args.org, args.verbose)
    elif args.command == "package":
        package_for_org(args.tools, args.output_dir, args.verbose)


if __name__ == "__main__":
    main()
