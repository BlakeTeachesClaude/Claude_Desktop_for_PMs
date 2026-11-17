# Install together

The only prerequisite is the ability to install software. Start with an empty machine. Explain the terminal, package managers and what each package does.

## Windows (PowerShell)

```powershell
winget --version
winget install --id Git.Git -e
winget install --id GitHub.cli -e
winget install --id Python.Python.3.13 -e
winget search --id GnuWin32.Make
winget install --id GnuWin32.Make -e
winget install --id Anthropic.Claude -e
```

If WinGet is missing, install Microsoft App Installer. Use an approved alternative package manager or the official download if necessary. Reopen PowerShell to refresh PATH. If make is unavailable, use the equivalent `python scripts/sync.py` and `python scripts/sync.py --sample` while resolving installation.

## macOS (Terminal)

Install Homebrew from https://brew.sh if absent; follow its shell setup instructions.

```sh
brew install git gh python make
brew install --cask claude
```

## Check installations

```sh
git --version
gh --version
make --version
python3 --version
```

On Windows check `python --version` instead. Open Claude Desktop, sign in or create an account, and confirm Cowork is available. Create a GitHub account if needed. Never share login tokens with the class or Claude. If your account cannot access Cowork or live GitHub, pair up and use the sample dataset.

Links: https://cli.github.com/ | https://brew.sh | https://claude.com/download | https://github.com/signup
