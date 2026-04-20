#!/bin/bash
# Install DevHive SDD Skills to OpenCode configuration

DEST_DIR=~/.config/opencode/skills

mkdir -p "$DEST_DIR"

echo "Copying DevHive SDD skills to $DEST_DIR..."
cp -r skills/devhive_* "$DEST_DIR/"

echo "Cleaning up old MCP-based devhive_workflow if present..."
rm -rf "$DEST_DIR/devhive_workflow"
rm -f "$DEST_DIR/devhive_workflow.md"

echo "Installation complete! You can now use the devhive-orchestrator skill in OpenCode."
