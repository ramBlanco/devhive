# DevHive: Skill-Driven Development (SDD) for OpenCode

DevHive is a fully autonomous AI software development pipeline designed specifically as a set of Skills and a dedicated Agent for **OpenCode**.

It replaces complex background servers and in-memory states with a transparent, predictable, and local **Skill-Driven Development (SDD)** architecture. DevHive uses your file system (`.devhive/specs/`) as its database, generating readable Markdown files at each step of the software lifecycle.

## The Pipeline

DevHive is composed of specialized Agent Skills that work sequentially:

0. **`devhive-prd`**: Acts as a Product Manager. Writes or updates a Master `docs/PRODUCT_REQUIREMENTS.md` and generates a feature-specific `.devhive/specs/00-prd.md` before any technical work begins.
1. **`devhive-explorer`**: Analyzes the PRD and codebase, then writes `.devhive/specs/01-exploration.md`
2. **`devhive-proposal`**: Creates technical acceptance criteria in `02-proposal.md`
3. **`devhive-architect`**: Designs the system architecture, DB schemas, and UX/UI design system in `03-architecture.md`
4. **`devhive-taskplanner`**: Breaks the architecture into actionable items across 8 different domains in `04-tasks.md`
5. **`devhive-designer`**: Implements the base UI/UX configuration (CSS vars, Tailwind configs) under `## Design Tasks`
6. **`devhive-devops`**: Writes Infrastructure as Code (IaC) (Terraform, CDK, Docker) and checks off `## Infrastructure Tasks`
7. **`devhive-dba`**: Creates DB schemas, migrations, and seeders under `## Data Tasks`
8. **`devhive-backender`**: Initializes the project, writes APIs and server logic, and checks off `## Backend Tasks`
9. **`devhive-frontender`**: Writes UI components and client-side logic, and checks off `## Frontend Tasks`
10. **`devhive-perf`**: Writes load testing scripts (k6, artillery) under `## Performance Tasks`
11. **`devhive-techwriter`**: Writes API docs (Swagger) and updates README under `## Documentation Tasks`
12. **`devhive-releaser`**: Bumps package versions, writes CHANGELOG, and creates local git tags under `## Release Tasks`
13. **`devhive-sast`**: Performs a Static Application Security Testing (SAST) scan and writes `05-sast-report.md`
14. **`devhive-qa`**: Writes test cases and test plans in `06-qa-plan.md`
15. **`devhive-auditor`**: Performs a final check and writes `07-audit.md`
16. **`devhive-reflection`**: Extracts persistent memory (semantic, episodic, anti-patterns) to `.devhive/memory/` and writes `08-reflection.md`

All of this is managed by the **`devhive-orchestrator`** skill.

## Product Planning Skills

DevHive bundles two skills for turning product requirements into reviewable user stories. They are available after `devhive install` or `devhive update-skill`. You can invoke them directly, and `@devhive-pm` also uses them in batch after generating a Feature PRD.

- **`devhive-backlog`**: Give it PRD text or a readable PRD path to get small, user-centered stories traceable to the source. It calls out important ambiguity rather than inventing requirements. Example: “Use `devhive-backlog` to break down `.devhive/specs/00-prd.md` into user stories.”
- **`devhive-story`**: Give it one selected story and, when useful, its source PRD/context. It returns exactly 2–3 Given/When/Then acceptance criteria and a mini plan of at most five bullets, then asks for review. Example: “Use `devhive-story` to refine US-001 from the approved backlog.”

When used directly, review the backlog before selecting a story for refinement. In the PM workflow, the agent collects all story results into one package and requests a single consolidated review. Approval is required before handoff and never executes a mini plan. These skills are distinct from the PM agent's prioritized `docs/PRODUCT/backlog.md` artifact (MoSCoW/RICE), which is for product-level prioritization rather than story details.

## The Agents

DevHive ships with two OpenCode agents:

### `@devhive` — The Software Engineer

Autonomous software development agent. Hardwired to immediately start the SDD pipeline.

```
@devhive Build a script that converts CSV to JSON running on AWS Lambda.
```

### `@devhive-pm` — The Product Manager

Standalone product layer that sits **above** the SDD pipeline. It defines *what* to build and *why*, then hands off to `@devhive` for *how*.

```
@devhive-pm We need a way for customers to track their support tickets.
```

The PM agent loads the bundled `devhive-prd`, `devhive-explorer`, `devhive-backlog`, and `devhive-story` skills. It creates the prioritized product backlog before story refinement, then produces at least one story for every in-scope `PM-###` item (multiple stories when an item represents independent outcomes). Each artifact cross-references `PM-###` and `US-###`; items marked `Won't have (this iteration)` do not require stories.

| Artifact | Contents |
| --- | --- |
| `docs/PRODUCT/product-vision.md` | Problem, audience, value proposition, principles, non-goals |
| `docs/PRODUCT/stakeholders.md` | Stakeholder map, influence/interest, engagement strategy |
| `docs/PRODUCT/metrics.md` | North Star metric, supporting KPIs, baselines and targets |
| `docs/PRODUCT/roadmap.md` | Now / Next / Later horizons with dependencies |
| `docs/PRODUCT/backlog.md` | Prioritized backlog (MoSCoW + RICE) with effort, value and risk, plus related `US-###` IDs |
| `docs/PRODUCT/user-stories.md` | Stories grouped by backlog item and PRD source, each with Given/When/Then criteria and a mini plan of up to five task bullets; package is Draft until explicitly approved |
| `docs/PRODUCT_REQUIREMENTS.md` | Master PRD (whole product) |
| `.devhive/specs/00-prd.md` | Feature PRD for the current cycle |

The PM agent never writes code. It asks for one consolidated review of the story package. After the user approves, it marks the package `Approved`; the user can then choose one unblocked story for implementation:

```
@devhive Implement story US-003 from backlog item PM-002 in the approved PM package. Read .devhive/specs/00-prd.md, docs/PRODUCT/backlog.md, and docs/PRODUCT/user-stories.md.
```

`@devhive` validates the selected story and maps only its backlog/story IDs and acceptance criteria into technical tasks in `.devhive/specs/04-tasks.md`; it asks for a story selection rather than defaulting to the first story or implementing the entire package. When invoked directly with no PM PRD/backlog/story package, it keeps the existing self-starting flow: creates its own Feature PRD, then runs the normal SDD phases. PM artifacts are optional inputs; Draft, stale, or conflicting packages are not silently treated as approved.

## Installation

DevHive is available as a Python package via PyPI. You can install it globally to manage your OpenCode skills across all your environments.

```bash
pip install devhive
```

Once installed, you can use the CLI to setup or update your DevHive environment:

```bash
# Install DevHive's bundled skills and agents into OpenCode
devhive install

# Update DevHive's bundled skills and agents to the latest versions
devhive update-skill

# Initialize a modern Next.js/React frontend AI guidelines file in your current project
devhive init-frontend

# Initialize a Hexagonal Architecture backend AI guidelines file (Interactive Prompt)
devhive init-backend
```

DevHive installs only the skills bundled inside this package. It does not download, search for, or install third-party skills from GitHub or other external sources.

The install and update commands also remove the previously installed external `shadcn` and `prd` skills, stale DevHive skill directories, remote skill URLs from the OpenCode configuration, and the obsolete DevHive plugin dependency. Other project-local skills under `.opencode/skills`, `.claude/skills`, `.agents/skills`, and `skills/` are preserved.

DevHive writes OpenCode 2 configuration under `agents.<agent>.permissions` and preserves unrelated user configuration. Only the `devhive` and `devhive-pm` agents receive the strict DevHive skill allowlist; other agents keep their existing permissions. The bundled `devhive-skills-only` plugin keeps DevHive's bundled skills, OpenCode built-ins, and project-local skills available while removing external skills from the skill catalog.

### Requirements

- Python 3.7 or newer
- OpenCode 2 (the bundled `devhive-skills-only` plugin uses the OpenCode 2 skill-transform API)

### Tests

Install the test dependencies and run the test suite:

```bash
pip install -e ".[test]"
pytest
```

## Usage (The `@devhive` Agent)

Instead of using OpenCode as a general assistant, invoke the dedicated `@devhive` agent. This agent is hardwired to immediately start the SDD pipeline.

```
@devhive Build a script that converts CSV to JSON running on AWS Lambda.
```

The agent will automatically load the orchestrator skill and start the 11-phase pipeline!

### Continuous Mode
By default, the orchestrator will pause and ask for your approval after writing each specification file (e.g., after writing the architecture design). If you want it to run entirely autonomously without stopping, you can add the "continuous mode" flag to your prompt:

```
@devhive Build a React landing page. Run in continuous mode with no pauses.
```

Or permanently enable it for the project by creating a flag file:
```bash
mkdir -p .devhive
touch .devhive/continuous
```

## Why SDD (Skill-Driven Development)?

- **Zero Setup**: No Python servers, no MCP configuration, no background processes.
- **Local Memory**: The entire state of the project is readable by humans in `.devhive/specs/`. You can edit `02-proposal.md` manually, and the Architect will adapt to your changes.
- **Modular**: Need a different architectural approach? You can just tweak the prompt inside `skills/devhive-architect/SKILL.md`.

## License

MIT License.
