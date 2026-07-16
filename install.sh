#!/usr/bin/env bash
# Agent Ninja installer
# Wires up hooks pointing to wherever you cloned this repo.
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_SOURCE="$SCRIPT_DIR/hooks/hooks.json"

echo "Agent Ninja installer"
echo "Repo path: $SCRIPT_DIR"
echo ""

# Check Python 3 is available
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required but not found on PATH."
  exit 1
fi

# Ask: global or project-level install
echo "Where do you want to install the hooks?"
echo "  1) Global  — ~/.claude/hooks.json (all Claude Code sessions)"
echo "  2) Project — .claude/hooks.json   (current directory only)"
echo ""
read -r -p "Enter 1 or 2: " choice

case "$choice" in
  1)
    HOOKS_DEST="$HOME/.claude/hooks.json"
    ;;
  2)
    HOOKS_DEST="$(pwd)/.claude/hooks.json"
    ;;
  *)
    echo "Invalid choice. Aborted."
    exit 1
    ;;
esac

echo ""
echo "Installing to: $HOOKS_DEST"

# Warn if hooks file already exists
if [ -f "$HOOKS_DEST" ]; then
  echo ""
  echo "Warning: $HOOKS_DEST already exists."
  read -r -p "Overwrite? (y/N) " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted. No changes made."
    exit 0
  fi
fi

# Create destination directory if it doesn't exist
mkdir -p "$(dirname "$HOOKS_DEST")"

# Write hooks.json with the correct absolute path substituted in
sed "s|\${CLAUDE_PLUGIN_ROOT}|$SCRIPT_DIR|g" "$HOOKS_SOURCE" > "$HOOKS_DEST"

echo ""
echo "Done! Hooks installed to $HOOKS_DEST"
echo ""
echo "Next steps:"
echo "  1. Add the Agent Ninja instructions to your CLAUDE.md"
echo "     See SETUP.md for the copy-paste block."
echo "  2. Start a Claude Code session and try a prompt."
echo "     You should see [Agent Ninja] context in the response."
