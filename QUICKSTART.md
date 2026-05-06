# Quick Start Guide

## Installation

1. Clone the GitHub Publisher repository:
```bash
git clone https://github.com/OpenSeneca/github-publisher.git ~/.openclaw/workspace/tools/github-publisher
```

2. Make scripts executable:
```bash
chmod +x ~/.openclaw/workspace/tools/github-publisher/publish.py
chmod +x ~/.openclaw/workspace/tools/github-publisher/publish-tool.sh
```

3. Install GitHub CLI (if not already installed):
```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh
```

4. Authenticate with GitHub:
```bash
gh auth login
```

## Publishing a Tool

### Using Python (Recommended)

```bash
cd ~/.openclaw/workspace/tools/github-publisher
python3 publish.py --name my-tool --description "My tool description" --version 1.0.0
```

### Using Bash

```bash
cd ~/.openclaw/workspace/tools/github-publisher
./publish-tool.sh --name my-tool --description "My tool description" --version 1.0.0
```

## Publishing Existing Tools

### blog-assistant
```bash
python3 publish.py \
  --name blog-assistant \
  --description "AI-powered blog writing assistant for squad operations" \
  --version 1.0.0
```

### squad-deployer
```bash
python3 publish.py \
  --name squad-deployer \
  --description "Automated deployment tool for squad infrastructure" \
  --version 1.0.0
```

### squad-ssh-manager
```bash
python3 publish.py \
  --name squad-ssh-manager \
  --description "SSH connection manager for squad servers" \
  --version 1.0.0
```

### forge-monitor
```bash
python3 publish.py \
  --name forge-monitor \
  --description "Monitoring tool for Forge server status" \
  --version 1.0.0
```

## Dry Run Mode

Preview commands without executing:

```bash
python3 publish.py --name my-tool --dry-run
```

## Requirements

- GitHub CLI (`gh`) installed
- Authenticated GitHub account with write access to OpenSeneca organization
- Tool directory must exist in `~/.openclaw/workspace/tools/`

## What Gets Published?

1. **README.md** - Auto-generated with standard template
2. **LICENSE** - MIT license added
3. **Git repository** - Initialized if needed
4. **GitHub repository** - Created in OpenSeneca organization
5. **Version tag** - Created and pushed (e.g., v1.0.0)

## Troubleshooting

### "Repository already exists"
This is normal. The tool will just push code and tag releases for existing repos.

### "GitHub CLI not found"
Install GitHub CLI: https://cli.github.com/

### "Write access denied"
Ensure you have write permissions in the OpenSeneca organization.

## Next Steps

After publishing, your tool is available at:
https://github.com/OpenSeneca/[tool-name]

You can now:
1. Add issues and milestones
2. Invite collaborators
3. Create releases with detailed changelogs
4. Set up CI/CD workflows
