# DevHive: Skill-Driven Development (SDD) for OpenCode

DevHive is a fully autonomous AI software development pipeline designed specifically as a set of Skills and a dedicated Agent for **OpenCode**.

It replaces complex background servers and in-memory states with a transparent, predictable, and local **Skill-Driven Development (SDD)** architecture. DevHive uses your file system (`.devhive/specs/`) as its database, generating readable Markdown files at each step of the software lifecycle.

## The Pipeline

DevHive is composed of specialized Agent Skills that work sequentially:

1. **`devhive-explorer`**: Analyzes the request and writes `.devhive/specs/01-exploration.md`
2. **`devhive-proposal`**: Creates acceptance criteria in `02-proposal.md`
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

All of this is managed by the **`devhive-orchestrator`** skill.

## Installation

DevHive is available as a Python package via PyPI. You can install it globally to manage your OpenCode skills across all your environments.

```bash
pip install devhive
```

Once installed, you can use the CLI to setup or update your DevHive environment:

```bash
# Install all official and community skills into OpenCode
devhive install

# Update your existing skills to the latest versions
devhive update-skill

# Initialize a modern Next.js/React frontend AI guidelines file in your current project
devhive init-frontend

# Initialize a Hexagonal Architecture backend AI guidelines file (Interactive Prompt)
devhive init-backend
```

## Usage (The `@devhive` Agent)

Instead of using OpenCode as a general assistant, invoke the dedicated `@devhive` agent. This agent is hardwired to immediately start the SDD pipeline.

```
@devhive Build a script that converts CSV to JSON running on AWS Lambda.
```

The agent will automatically load the orchestrator skill and start the 10-phase pipeline!

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
- **Modular**: Need a different architectural approach? You can just tweak the prompt inside `skills/devhive_architect/SKILL.md`.

## License

MIT License.
