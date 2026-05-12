#!/usr/bin/env python3
"""
GitHub Publisher - Publish OpenSeneca tools to PyPI

This tool automates the process of publishing OpenSeneca tools to PyPI.
It handles:
- Building distribution packages (wheel and sdist)
- Publishing to PyPI
- Version management
- GitHub repository setup

Usage:
    python3 main.py --tool squad-ssh-manager --publish
    python3 main.py --tool squad-deployer --publish
    python3 main.py --list-tools
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
import json
import re
from typing import List, Dict, Optional

# Base workspace directory
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace" / "tools"

# Known OpenSeneca tools that can be published
KNOWN_TOOLS = [
    "squad-ssh-manager",
    "squad-deployer",
    "squad-content-pipeline",
    "squad-activity-digest",
    "blog-assistant",
    "auto-ingester",
    "squad-config-validator",
    "squad-tool-deployer",
]


class GitHubPublisher:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.workspace_dir = WORKSPACE_DIR

    def log(self, message: str):
        """Print log message if verbose."""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        self.log(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.log(f"Command failed with exit code {result.returncode}")
            self.log(f"STDERR: {result.stderr}")
        return result.returncode, result.stdout, result.stderr

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools with their status."""
        tools = []
        for tool_name in KNOWN_TOOLS:
            tool_path = self.workspace_dir / tool_name
            if tool_path.exists():
                status = self._get_tool_status(tool_path, tool_name)
                tools.append({
                    "name": tool_name,
                    "path": str(tool_path),
                    "has_setup": status["has_setup"],
                    "has_dist": status["has_dist"],
                    "has_git": status["has_git"],
                    "has_remote": status["has_remote"],
                    "version": status["version"]
                })
        return tools

    def _get_tool_status(self, tool_path: Path, tool_name: str) -> Dict[str, any]:
        """Get the status of a tool."""
        status = {
            "has_setup": False,
            "has_dist": False,
            "has_git": False,
            "has_remote": False,
            "version": None
        }

        # Check for setup.py
        if (tool_path / "setup.py").exists():
            status["has_setup"] = True
            # Extract version from setup.py
            try:
                with open(tool_path / "setup.py", 'r') as f:
                    content = f.read()
                    version_match = re.search(r'version="([^"]+)"', content)
                    if version_match:
                        status["version"] = version_match.group(1)
            except Exception:
                pass

        # Check for dist directory
        dist_dir = tool_path / "dist"
        if dist_dir.exists() and list(dist_dir.glob("*.whl")):
            status["has_dist"] = True

        # Check for git
        if (tool_path / ".git").exists():
            status["has_git"] = True
            # Check for remote
            try:
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=tool_path,
                    capture_output=True,
                    text=True
                )
                if "origin" in result.stdout:
                    status["has_remote"] = True
            except Exception:
                pass

        return status

    def build_package(self, tool_name: str) -> bool:
        """Build distribution packages for a tool."""
        tool_path = self.workspace_dir / tool_name
        if not tool_path.exists():
            print(f"Error: Tool {tool_name} not found at {tool_path}", file=sys.stderr)
            return False

        print(f"Building package for {tool_name}...")

        # Clean old dist
        dist_dir = tool_path / "dist"
        if dist_dir.exists():
            self.log(f"Cleaning old dist directory")
            subprocess.run(["rm", "-rf", str(dist_dir)])

        # Build source distribution and wheel
        code, stdout, stderr = self.run_command(
            [sys.executable, "-m", "build", "--wheel", "--sdist"],
            cwd=tool_path
        )

        if code != 0:
            print(f"Error building package for {tool_name}", file=sys.stderr)
            print(f"STDERR: {stderr}", file=sys.stderr)
            return False

        print(f"✓ Successfully built {tool_name}")
        return True

    def publish_to_pypi(self, tool_name: str, test_pypi: bool = False) -> bool:
        """Publish a tool to PyPI."""
        tool_path = self.workspace_dir / tool_name
        if not tool_path.exists():
            print(f"Error: Tool {tool_name} not found at {tool_path}", file=sys.stderr)
            return False

        # Check if dist exists
        dist_dir = tool_path / "dist"
        if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
            print(f"Error: No distribution packages found for {tool_name}", file=sys.stderr)
            print(f"Run build first: python3 main.py --tool {tool_name} --build", file=sys.stderr)
            return False

        print(f"Publishing {tool_name} to {'Test' if test_pypi else 'PyPI'}...")

        # Check if twine is installed
        try:
            subprocess.run(["twine", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: twine is not installed. Install it with: pip install twine build", file=sys.stderr)
            return False

        # Check if .pypirc exists or token is configured
        # We'll let twine handle authentication - user should have configured it

        # Publish
        cmd = ["twine", "upload"]
        if test_pypi:
            cmd.extend(["--repository", "testpypi"])
        cmd.extend(["--skip-existing", "dist/*"])

        code, stdout, stderr = self.run_command(cmd, cwd=tool_path)

        if code != 0:
            print(f"Error publishing {tool_name}", file=sys.stderr)
            print(f"STDERR: {stderr}", file=sys.stderr)
            return False

        print(f"✓ Successfully published {tool_name} to {'Test' if test_pypi else 'PyPI'}")
        return True

    def setup_github_repo(self, tool_name: str) -> bool:
        """Set up GitHub repository for a tool."""
        tool_path = self.workspace_dir / tool_name
        if not tool_path.exists():
            print(f"Error: Tool {tool_name} not found at {tool_path}", file=sys.stderr)
            return False

        print(f"Setting up GitHub repository for {tool_name}...")

        # Check if git is initialized
        if not (tool_path / ".git").exists():
            self.log(f"Initializing git repository")
            code, _, stderr = self.run_command(["git", "init"], cwd=tool_path)
            if code != 0:
                print(f"Error initializing git: {stderr}", file=sys.stderr)
                return False

        # Check if remote exists
        code, stdout, _ = self.run_command(["git", "remote", "-v"], cwd=tool_path)
        if "origin" not in stdout:
            # Create remote URL
            repo_url = f"https://github.com/OpenSeneca/{tool_name}.git"
            print(f"Adding remote: {repo_url}")
            code, _, stderr = self.run_command(
                ["git", "remote", "add", "origin", repo_url],
                cwd=tool_path
            )
            if code != 0:
                print(f"Error adding remote: {stderr}", file=sys.stderr)
                return False

        # Check if there's a README
        if not (tool_path / "README.md").exists():
            print(f"Warning: No README.md found in {tool_name}", file=sys.stderr)

        print(f"✓ GitHub repository set up for {tool_name}")
        print(f"  Remote: https://github.com/OpenSeneca/{tool_name}.git")
        print(f"  Next steps:")
        print(f"    1. Create the repository on GitHub: https://github.com/new")
        print(f"    2. Push: cd {tool_path} && git push -u origin main")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Publisher - Publish OpenSeneca tools to PyPI"
    )
    parser.add_argument(
        "--tool", "-t",
        help="Tool name to publish"
    )
    parser.add_argument(
        "--list-tools", "-l",
        action="store_true",
        help="List all available tools"
    )
    parser.add_argument(
        "--build", "-b",
        action="store_true",
        help="Build distribution packages"
    )
    parser.add_argument(
        "--publish", "-p",
        action="store_true",
        help="Publish to PyPI"
    )
    parser.add_argument(
        "--test-pypi",
        action="store_true",
        help="Publish to Test PyPI instead of production"
    )
    parser.add_argument(
        "--setup-github", "-g",
        action="store_true",
        help="Set up GitHub repository"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    publisher = GitHubPublisher(verbose=args.verbose)

    # List tools
    if args.list_tools:
        tools = publisher.list_tools()
        print("\nOpenSeneca Tools:")
        print("=" * 80)
        for tool in tools:
            print(f"\n{tool['name']}")
            print(f"  Path: {tool['path']}")
            print(f"  Version: {tool['version'] or 'N/A'}")
            print(f"  Setup.py: {'✓' if tool['has_setup'] else '✗'}")
            print(f"  Dist: {'✓' if tool['has_dist'] else '✗'}")
            print(f"  Git: {'✓' if tool['has_git'] else '✗'}")
            print(f"  Remote: {'✓' if tool['has_remote'] else '✗'}")
        return 0

    # Require --tool for other operations
    if not args.tool:
        print("Error: --tool is required for this operation", file=sys.stderr)
        print("Use --list-tools to see available tools", file=sys.stderr)
        return 1

    # Setup GitHub repository
    if args.setup_github:
        if not publisher.setup_github_repo(args.tool):
            return 1

    # Build package
    if args.build:
        if not publisher.build_package(args.tool):
            return 1

    # Publish to PyPI
    if args.publish:
        if not publisher.publish_to_pypi(args.tool, test_pypi=args.test_pypi):
            return 1

    # If no action specified, show tool status
    if not (args.build or args.publish or args.setup_github):
        tools = publisher.list_tools()
        tool = next((t for t in tools if t["name"] == args.tool), None)
        if tool:
            print(f"\n{tool['name']}")
            print(f"  Path: {tool['path']}")
            print(f"  Version: {tool['version'] or 'N/A'}")
            print(f"  Setup.py: {'✓' if tool['has_setup'] else '✗'}")
            print(f"  Dist: {'✓' if tool['has_dist'] else '✗'}")
            print(f"  Git: {'✓' if tool['has_git'] else '✗'}")
            print(f"  Remote: {'✓' if tool['has_remote'] else '✗'}")
            print(f"\nActions:")
            print(f"  python3 main.py --tool {args.tool} --setup-github")
            print(f"  python3 main.py --tool {args.tool} --build")
            print(f"  python3 main.py --tool {args.tool} --publish")
            print(f"  python3 main.py --tool {args.tool} --publish --test-pypi")
        else:
            print(f"Error: Tool {args.tool} not found", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
