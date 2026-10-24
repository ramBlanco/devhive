# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.45] - 2026-10-24

### Added,

- backlog and user story

## [0.1.44] - 2026-10-24

### Added,

- backlog and story for small tickets and task

## [0.1.43] - 2026-10-24

### Removed
- Removed automatic installation of third-party skills (`shadcn` and `prd`) from `devhive install` and `devhive update-skill`.
- DevHive now installs only the skills and agents bundled with the package.
- Removed runtime dependencies and instructions for external skills, including shadcn and awesome-copilot.
- Added the `devhive-skills-only` OpenCode 2 plugin to keep DevHive's bundled skills, OpenCode built-ins, and project-local skills while filtering external skills.
- Skill access restrictions now use OpenCode 2's `agents.<agent>.permissions` format and apply only to the `devhive` and `devhive-pm` agents; other OpenCode agents keep their existing permissions.
- Install and update now remove stale external skill directories, remote skill URLs from the OpenCode configuration, obsolete DevHive skill directories, and the obsolete DevHive plugin dependency.
- Removed the obsolete `skills-lock.json` file.
- Added automated tests covering bundled-only installation, external skill cleanup, agent permissions, and the absence of external installers.


## [0.1.42] - 2026-10-24

### Removed
- **Zero-Touch Policy**: The "🛑 SYSTEM DIRECTIVE: ZERO-TOUCH POLICY" block that forbade AI agents from writing code directly (and forced delegation to the DevHive orchestrator) has been removed entirely.
  - Deleted the `ZERO_TOUCH_POLICY` constant and the injection logic from `devhive_cli/main.py`.
  - Stripped the directive from the `AGENTS.frontend.md` and `AGENTS.backend.md` templates, so newly generated guidance files no longer contain it.
  - `devhive init-frontend` / `devhive init-backend` now **refuse to run** when an `AGENTS.md` already exists: the existing file is never overwritten, never injected into, and never modified in any way. The user is asked to delete or rename it manually.
  - The `devhive-explorer` and `devhive-analyzer` skills no longer create or enhance `GUIDELINES.md` in the project root. When no guidance file exists, the detected stack is reported in the phase output and persisted only inside `.devhive/memory/`.

### Changed
- **`devhive init-frontend` / `devhive init-backend`**: These commands are now strictly non-destructive — they only ever create a guidance file in a directory where none exists.

## [0.1.41] - 2026-10-24

### Added
- **`devhive-pm` Agent**: New standalone Product Manager agent for OpenCode, installed automatically via `devhive install` / `devhive update-skill`.
  - Operates as the product layer above the SDD pipeline: defines *what* to build and *why*, hands off to `@devhive` for *how*.
  - Loads the `prd` (awesome-copilot), `devhive-prd` and `devhive-explorer` skills, with graceful degradation when the optional remote `prd` skill is not installed.
  - Produces product artifacts under `docs/PRODUCT/`: `product-vision.md`, `stakeholders.md`, `metrics.md`, `roadmap.md` and `backlog.md` (MoSCoW + RICE prioritization).
  - Maintains the existing Hybrid PRD contract by writing `docs/PRODUCT_REQUIREMENTS.md` (Master PRD) and `.devhive/specs/00-prd.md` (Feature PRD).
  - Ends with an explicit handoff command for the SDD pipeline, avoiding re-discovery.
  - Strictly scoped to documentation: never writes code or makes architecture decisions.

### Fixed
- **Skill IDs no longer resolvable**: OpenCode derives a skill's ID from its **directory path**, and the `name` field in `SKILL.md` frontmatter is only a display name. The DevHive skill directories used underscores (`devhive_prd/`) while every `SKILL.md` declared `name: devhive-prd`, so the `skill` tool could not load them by the name referenced throughout the pipeline. All 19 DevHive skill directories are now hyphenated (`devhive-prd/`, `devhive-orchestrator/`, ...), matching their declared names, so `skill("devhive-prd")` and `skill("devhive-orchestrator")` now resolve correctly.
  - The community skill `backend-arthitect` was renamed to `backend-architect` for the same reason.
  - `devhive install` and `devhive update-skill` now remove the legacy underscore-named directories from the target skills folder so stale duplicates cannot shadow the corrected ones.

### Changed
- **README**: Documented the two available agents (`@devhive` and `@devhive-pm`) and the artifact set produced by the PM.

## [0.1.40] - 2026-06-05

### Added
- **devhive-analyzer Skill (Phase 0)**: New pre-orchestrator skill that runs before the SDD pipeline to analyze existing projects and propose memory entries for user approval.
  - Analyzes `AGENTS.md`, `GUIDELINES.md`, package.json, and codebase structure
  - Detects tech stack (FastAPI, Next.js, NestJS, etc.)
  - Detects architecture patterns (Hexagonal, Feature-based, MVC, etc.)
  - Extracts conventions and rules from existing documentation
  - Proposes semantic and anti-pattern memories for user approval
  - Only runs on first-time projects (when `.devhive/memory/` is empty)

- **Orchestrator Phase 0 Integration**: Updated `devhive-orchestrator` to invoke `devhive-analyzer` as the first step when no prior memory exists.

- **AGENTS.md Memory Extraction**: The analyzer now prioritizes extracting memories from `AGENTS.md` when it exists, as it contains explicit project rules and conventions with high confidence.

## [0.1.39] - 2026-06-05

### Added
- **Memory CLI System**: New `devhive memory` command group with full CRUD operations for managing persistent memory entries.
  - `devhive memory list` - List all memory entries with ID, type, score, and tags
  - `devhive memory show` - Show entries filtered by memory type
  - `devhive memory search <query>` - Search memories by text or tags
  - `devhive memory info <id>` - Show detailed info for a specific entry
  - `devhive memory delete <id>` - Delete a memory entry
  - `devhive memory stats` - Show memory statistics (counts, scores, tags)
  - `devhive memory export` - Export memories to JSON file
  - `devhive memory import` - Import memories from JSON file
  - `devhive memory gc` - Garbage collect entries below score threshold

- **Indexed Memory Architecture**: Memory entries now have unique IDs (sem-001, epi-001, ant-001) and are indexed in `.devhive/memory/index.json` for fast lookup and search.

- **Memory Tag System**: Each memory entry now supports tags for filtering and categorization (architecture, backend, bug, fix, security, etc.).

- **Updated Skills for Memory Access**: All memory-consuming skills (explorer, architect, taskplanner, backender, frontender, auditor) now have improved memory access patterns with tag-based filtering and index-first loading.

- **devhive-reflection Enhanced**: The reflection skill now maintains the index.json and uses ID references when writing memories.

## [0.1.38] - 2026-04-29

### Fixed
- **Import Resolution**: Fixed a `NameError` related to the `Path` object in `devhive_cli/main.py`. The imports (including `pathlib.Path`, `click`, etc.) were reorganized and hoisted to the absolute top of the file to ensure they are properly initialized before being utilized by the `handle_existing_agents_md` helper function.

## [0.1.37] - 2026-04-29

### Fixed
- **CLI Syntax Error**: Fixed a critical `SyntaxError` (unterminated string literal) in `devhive_cli/main.py` caused by unescaped newlines in the interactive `init` prompt. The `devhive init-backend` and `devhive init-frontend` commands now work correctly when an `AGENTS.md` file already exists.

## [0.1.36] - 2026-04-29

### Changed
- **Zero-Touch Policy Injection**: Enhanced the `devhive init-frontend` and `devhive init-backend` commands. If an `AGENTS.md` file already exists, the CLI will now check if the Zero-Touch Policy is present. If it's missing, it will prompt the user with options to automatically inject the policy at the top of their existing file, overwrite it completely, or abort, ensuring legacy projects can easily adopt the DevHive enforcement rules without losing custom guidelines.

## [0.1.35] - 2026-04-29

### Added
- **Persistent Memory System (Phase 1)**: Transformed DevHive from a stateless orchestrator into a "Persistent Learning Agent Ecosystem". 
  - Introduced the `devhive-reflection` skill (Phase 16) which runs at the end of each cycle to extract, score, and deduplicate learnings from execution and human feedback.
  - Added semantic (`semantic.md`), episodic (`episodic.md`), and anti-pattern (`anti_patterns.md`) memory storage in the `.devhive/memory/` directory.
  - Updated all planning agents (`explorer`, `architect`, `taskplanner`) to consume semantic and anti-pattern memories to enforce historical project constraints.
  - Updated executor agents (`frontender`, `backender`) to consume episodic memory to avoid repeating bugs.
  - Updated the orchestrator to inject chat history into the reflection agent for capturing human corrections.

## [0.1.34] - 2026-04-29

### Added
- **Zero-Touch Policy (DevHive Enforcement)**: Injected a critical system directive into the `AGENTS.frontend.md` and `AGENTS.backend.md` templates. This explicitly forbids generic AI agents from directly modifying source code when presented with a feature request, forcing them to delegate all implementation work to the `devhive-orchestrator` pipeline.

## [0.1.33] - 2026-04-29

### Added
- **Executive Summary Dashboard**: Enhanced the `devhive-orchestrator` completion phase. When the pipeline finishes, the orchestrator now automatically reads the SAST (`05-sast-report.md`) and Audit (`07-audit.md`) reports to present the user with a highly visible Markdown table summarizing security vulnerabilities and an overview of the auditor's findings (Pass/Fail status, architecture adherence) directly in the chat interface.

## [0.1.32] - 2026-04-29

### Changed
- **Strict Plan Ingestion**: Updated the core `devhive` agent and `devhive-orchestrator` to explicitly forbid skipping SDD phases. When a user provides a pre-made plan or detailed context, the agent will now ingest it as input and systematically run through all planning phases (`prd`, `explorer`, `proposal`, `architect`, `taskplanner`) to formalize the plan into `.devhive/specs/` artifacts instead of jumping straight to coding.

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
