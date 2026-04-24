#!/bin/bash
# Sync Community Skills and Remote Skills to OpenCode configuration

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

echo "Installing official remote skills via skills.sh..."
# Install shadcn skill using non-interactive flags
npx --yes skills add https://github.com/shadcn/ui --skill shadcn -y --global

npx --yes skills add https://github.com/supercent-io/skills-template --skill responsive-design -y --global

# Ensure the downloaded skill is explicitly copied to the opencode directory
if [ -d "$HOME/.agents/skills/shadcn" ]; then
    echo "Copying shadcn skill to OpenCode..."
    cp -r "$HOME/.agents/skills/shadcn" "$SKILLS_DIR/"
    echo "Remote skills installed and synced successfully."
else
    echo "Warning: shadcn skill was not found in ~/.agents/skills/shadcn."
fi
