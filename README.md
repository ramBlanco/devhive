# DevHive: Skill-Driven Development (SDD) for OpenCode

DevHive is a fully autonomous AI software development pipeline designed specifically as a set of Skills and a dedicated Agent for **OpenCode**.

It replaces complex background servers and in-memory states with a transparent, predictable, and local **Skill-Driven Development (SDD)** architecture. DevHive uses your file system (`.devhive/specs/`) as its database, generating readable Markdown files at each step of the software lifecycle.

## The Pipeline

DevHive is composed of specialized Agent Skills that work sequentially:

1. **`devhive-explorer`**: Analyzes the request and writes `.devhive/specs/01-exploration.md`
2. **`devhive-proposal`**: Creates acceptance criteria in `02-proposal.md`
3. **`devhive-architect`**: Designs the system architecture and cloud infrastructure in `03-architecture.md`
4. **`devhive-taskplanner`**: Breaks the architecture into actionable items, separating infrastructure, backend, and frontend code in `04-tasks.md`
5. **`devhive-devops`**: Writes Infrastructure as Code (IaC) (Terraform, CDK, Docker) and checks off `## Infrastructure Tasks` in `04-tasks.md`
6. **`devhive-backender`**: Initializes the project, writes APIs and server logic, and checks off `## Backend Tasks` in `04-tasks.md`
7. **`devhive-frontender`**: Writes UI components and client-side logic to consume the APIs, and checks off `## Frontend Tasks` in `04-tasks.md`
8. **`devhive-sast`**: Performs a Static Application Security Testing (SAST) scan and writes `05-sast-report.md`
9. **`devhive-qa`**: Writes test cases and test plans in `06-qa-plan.md`
10. **`devhive-auditor`**: Performs a final check and writes `07-audit.md`

All of this is managed by the **`devhive-orchestrator`** skill.

## Installation

To use DevHive in your OpenCode environment, run the install script. It will copy the skills and the `@devhive` agent profile into your local OpenCode configuration folder (`~/.config/opencode/`).

```bash
./install.sh
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
