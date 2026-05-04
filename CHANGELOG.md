# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.31] - 2026-04-29

### Changed
- **`devhive-frontender` Skill**: Added strict constraints to prevent the AI from manually building UI primitives from scratch. The agent is now explicitly forced to read `components.json` and use the `shadcn` CLI (or the `shadcn` skill) to install components before attempting to build custom UI elements, ensuring consistent design systems and avoiding "reinventing the wheel".

## [0.1.30] - 2026-04-29

### Added
- **Remote PRD Skill**: Integrated the `awesome-copilot` PRD skill as a remote dependency (installed via `npx`). The `devhive-prd` agent now automatically invokes this remote skill to leverage the official GitHub PRD formatting guidelines.

## [0.1.29] - 2026-04-29

### Added
- **`devhive-prd` Skill**: Introduced a Product Requirements Document (PRD) phase (Step 0). It uses a hybrid approach, creating/updating a Master `docs/PRODUCT_REQUIREMENTS.md` via reverse engineering of the codebase, and a feature-specific `.devhive/specs/00-prd.md` before technical exploration starts. Based on GitHub's awesome-copilot PRD templates.
- **Orchestrator Update**: Integrated `devhive-prd` into the main `devhive-orchestrator` pipeline as the initial step.
- **Explorer Update**: Updated `devhive-explorer` to read and understand the PRD files before beginning technical exploration.

## [0.1.28] - 2026-04-28

### Fixed
- **PyPI Packaging Issue**: Moved static asset directories (`skills/`, `community_skills/`, `agents/`, `templates/`) into the `devhive_cli` Python module. This ensures that `setuptools` correctly bundles these files into the distributed `.whl` package on PyPI, fixing the bug where `devhive install` could not find them on user machines (e.g., on macOS).

## [0.1.27] - 2026-04-28

### Added
- **Agent Installation**: `devhive install` and `devhive update-skill` now automatically sync the `@devhive` agent definition file to the OpenCode `~/.config/opencode/agents/` global directory.
- **Agent Prompt Enhancement**: Rewrote the `@devhive` agent prompt to enforce stricter lifecycle management (zero chatter), proactive execution of the `devhive-orchestrator` skill, and proper handling of "continuous mode".

### Removed
- **Responsive Design Skill**: Removed the remote installation of the `responsive-design` skill via npx, as the repository is no longer available.

## [0.1.26] - 2026-04-27

### Changed
- **Backend Template Refactoring**: Extracted the backend `AGENTS.md` guidelines string from Python code into a dedicated physical Markdown template file (`templates/AGENTS.backend.md`). The `devhive init-backend` command now dynamically injects stack selections into this file.

## [0.1.25] - 2026-04-27

### Added
- **Backend Template Command**: Added the `devhive init-backend` interactive command. It prompts the user for their preferred language (Node.js/Python), framework (FastAPI, Django, Express, NestJS, etc.), and IaC tool (CDK, Terraform, Serverless). It dynamically generates an `AGENTS.md` file enforcing strict Hexagonal Architecture, Dependency Injection (including InversifyJS examples), and Clean Code practices tailored to the chosen stack.

## [0.1.24] - 2026-04-27

### Added
- **Frontend Template Command**: Added the `devhive init-frontend` command to generate an `AGENTS.md` guidelines template for modern React 19 / Next.js 15 apps (with Server Actions and shadcn/ui). This explicitly instructs AI agents on standardizing architectural rules and code structure.

## [0.1.23] - 2026-04-24

### Changed
- **Modularity Fix**: Updated the `devhive_taskplanner` prompt to clearly support skipping unneeded domains (e.g., skipping Backend for Frontend-only projects) by explicitly omitting checkboxes.

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
