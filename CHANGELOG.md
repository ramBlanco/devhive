# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
