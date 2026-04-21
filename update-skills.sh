#!/bin/bash
# Sync Community Skills to OpenCode configuration

CONFIG_DIR=~/.config/opencode
SKILLS_DIR="$CONFIG_DIR/skills"

echo "Syncing community support skills..."
if [ -d "community_skills" ]; then
    for skill_dir in community_skills/*; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            echo "Installing community skill: $skill_name"
            cp -r "$skill_dir" "$SKILLS_DIR/"
        fi
    done
    echo "Community skills synced successfully."
else
    echo "Warning: community_skills directory not found."
fi
