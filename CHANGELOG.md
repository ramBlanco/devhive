# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.22] - 2026-04-24

### Added
- **Python CLI Tool**: Introduced a new `devhive` CLI tool installable via `pip`.
- Added `devhive install` command to automatically install all core and community skills to OpenCode.
- Added `devhive update-skill` command to cleanly update and re-sync installed skills.
- Added 6 new community skills: `architecture-patterns`, `backend-architect`, `backend-security-coder`, `docker-expert`, `frontend-developer`, and `theme-factory`.
- Hardcoded integrations of the new community skills into the core `devhive-*` agents (`devhive-architect`, `devhive-backender`, `devhive-devops`, and `devhive-frontender`).

### Removed
- Removed empty/useless community skills (e.g., `a11y-wcag-validator`, `clean-code`, `cloud-architect`, etc.) to clean up the ecosystem.
- Removed the deprecated `update-skills.sh` script in favor of the new Python CLI.

### Fixed
- Fixed hardcoded skill references in core DevHive agents that were pointing to removed community skills.
- Changed installation of remote dependencies (like `shadcn` and `responsive-design`) to be global across all AI tools (OpenCode, GitHub Copilot, Cursor).
