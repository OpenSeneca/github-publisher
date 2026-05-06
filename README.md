# GitHub Publisher

Automated tool publishing for OpenSeneca GitHub organization. Simplifies the process of creating repositories, pushing code, and tagging releases.

## Features

- Creates GitHub repositories in OpenSeneca organization
- Generates README.md with standard template
- Initializes git repository
- Creates and pushes version tags
- Supports dry-run mode for testing

## Installation

```bash
# Make the script executable (already done)
chmod +x publish-tool.sh

# Optional: Create symlink in PATH
ln -s ~/.openclaw/workspace/tools/github-publisher/publish-tool.sh ~/.local/bin/publishtool
```

## Usage

### Basic Usage

```bash
./publish-tool.sh --name my-tool --description "My awesome tool"
```

### With Version

```bash
./publish-tool.sh --name my-tool --description "My awesome tool" --version 2.0.0
```

### Dry Run (Preview Commands)

```bash
./publish-tool.sh --name my-tool --description "My awesome tool" --dry-run
```

### Options

| Option | Description |
|--------|-------------|
| `-n, --name NAME` | Tool name (required) |
| `-d, --description DESC` | Tool description |
| `-v, --version VERSION` | Version (default: 1.0.0) |
| `--dry-run` | Print commands without executing |
| `-h, --help` | Show help |

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Write access to OpenSeneca GitHub organization

## Examples

### Publish blog-assistant

```bash
./publish-tool.sh \
  --name blog-assistant \
  --description "AI-powered blog writing assistant for squad operations" \
  --version 1.0.0
```

### Publish squad-deployer

```bash
./publish-tool.sh \
  --name squad-deployer \
  --description "Automated deployment tool for squad infrastructure" \
  --version 1.0.0
```

## How It Works

1. Validates tool directory exists in `~/.openclaw/workspace/tools/`
2. Creates or updates README.md with standard template
3. Initializes git repository if not already initialized
4. Creates GitHub repository via GitHub CLI
5. Tags and pushes version release

## Repository Structure After Publishing

```
OpenSeneca/my-tool/
├── .git/           # Git repository
├── README.md       # Generated README
├── main.py/js/sh   # Tool entry point
└── ...            # Other tool files
```

## Troubleshooting

### "GitHub CLI (gh) not found"

Install GitHub CLI:
```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Or visit: https://cli.github.com/
```

Authenticate:
```bash
gh auth login
```

### "Tool directory not found"

Ensure the tool exists in `~/.openclaw/workspace/tools/`:
```bash
ls ~/.openclaw/workspace/tools/
```

### "Write access to OpenSeneca GitHub organization"

Ensure you have write permissions in the OpenSeneca organization. Contact an admin if needed.

## License

MIT License
