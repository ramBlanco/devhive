#!/bin/bash
# Install DevHive SDD Skills and Agent to OpenCode configuration

CONFIG_DIR=~/.config/opencode
SKILLS_DIR="$CONFIG_DIR/skills"
AGENTS_DIR="$CONFIG_DIR/agents"

mkdir -p "$SKILLS_DIR"
mkdir -p "$AGENTS_DIR"

echo "Copying DevHive SDD skills to $SKILLS_DIR..."
cp -r skills/devhive_* "$SKILLS_DIR/"

echo "Copying DevHive Agent to $AGENTS_DIR..."
cp agents/devhive.md "$AGENTS_DIR/" 2>/dev/null || echo "Warning: agents/devhive.md not found locally, skipping agent installation."

echo "Cleaning up old MCP-based devhive_workflow if present..."
rm -rf "$SKILLS_DIR/devhive_workflow"
rm -f "$SKILLS_DIR/devhive_workflow.md"

echo "Installation complete! You can now use the @devhive agent in OpenCode."
