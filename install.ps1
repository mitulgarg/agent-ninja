# Agent Ninja installer for Windows (PowerShell)
# Wires up hooks pointing to wherever you cloned this repo.
# Usage: .\install.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$HooksSource = Join-Path $ScriptDir "hooks\hooks.json"

Write-Host "Agent Ninja installer"
Write-Host "Repo path: $ScriptDir"
Write-Host ""

# Check Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and
    -not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "Error: python or python3 is required but not found on PATH." -ForegroundColor Red
    exit 1
}

# Determine which python command to use
$PythonCmd = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }

# Ask: global or project-level install
Write-Host "Where do you want to install the hooks?"
Write-Host "  1) Global  - $env:USERPROFILE\.claude\hooks.json (all Claude Code sessions)"
Write-Host "  2) Project - .claude\hooks.json                  (current directory only)"
Write-Host ""
$choice = Read-Host "Enter 1 or 2"

switch ($choice) {
    "1" { $HooksDest = Join-Path $env:USERPROFILE ".claude\hooks.json" }
    "2" { $HooksDest = Join-Path (Get-Location) ".claude\hooks.json" }
    default {
        Write-Host "Invalid choice. Aborted." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Installing to: $HooksDest"

# Warn if hooks file already exists
if (Test-Path $HooksDest) {
    Write-Host ""
    Write-Host "Warning: $HooksDest already exists." -ForegroundColor Yellow
    $confirm = Read-Host "Overwrite? (y/N)"
    if ($confirm -notmatch "^[Yy]$") {
        Write-Host "Aborted. No changes made."
        exit 0
    }
}

# Create destination directory if it doesn't exist
$DestDir = Split-Path -Parent $HooksDest
if (-not (Test-Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir | Out-Null
}

# Read hooks template and substitute the repo path
# Use forward slashes in the path so Python can read it cross-platform
$RepoPath = $ScriptDir -replace "\\", "/"
$HooksContent = Get-Content $HooksSource -Raw
$HooksContent = $HooksContent -replace [regex]::Escape('${CLAUDE_PLUGIN_ROOT}'), $RepoPath

# Patch python command if needed (replace python3 with python on systems without python3)
if ($PythonCmd -eq "python") {
    $HooksContent = $HooksContent -replace "python3 ", "python "
}

Set-Content -Path $HooksDest -Value $HooksContent -Encoding UTF8

Write-Host ""
Write-Host "Done! Hooks installed to $HooksDest" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Add the Agent Ninja instructions to your CLAUDE.md"
Write-Host "     See INSTALL.md for the copy-paste block."
Write-Host "  2. Start a Claude Code session and try a prompt."
Write-Host "     You should see [Agent Ninja] context in the response."