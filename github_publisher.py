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
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TOOLS_DIR = WORKSPACE / "tools"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

# Tool patterns to ignore
IGNORED_TOOLS = {"archive", "node_modules", "__pycache__", "_archive-"}


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


def list_tools(verbose: bool = False):
    """List all discoverable tools with their metadata."""
    tools = discover_tools(TOOLS_DIR)

    if not tools:
        print("No tools found.")
        return

    print(f"\nFound {len(tools)} tools:\n")

    for tool_path in tools:
        info = get_tool_info(tool_path)
        print(f"📦 {info['name']}")
        print(f"   Version: {info['version'] or 'Unknown'}")
        print(f"   Path: {info['path']}")
        print(f"   Git: {'✅' if info['has_git'] else '❌'}")
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


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Publisher - Automate building and publishing squad tools"
    )
    parser.add_argument(
        "command",
        choices=["list", "build", "publish", "release"],
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
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="GitHub Publisher v1.0.0"
    )

    args = parser.parse_args()

    if args.command == "list":
        list_tools(args.verbose)
    elif args.command == "build":
        build_all(args.tools, args.verbose)
    elif args.command == "publish":
        publish_all(args.tools, args.token, args.verbose)
    elif args.command == "release":
        release_all(args.tools, args.verbose)


if __name__ == "__main__":
    main()
