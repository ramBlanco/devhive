# DevHive: Skill-Driven Development (SDD) for OpenCode

DevHive is a fully autonomous AI software development pipeline designed specifically as a set of Skills for **OpenCode**.

It replaces complex background servers and in-memory states with a transparent, predictable, and local **Skill-Driven Development (SDD)** architecture. DevHive uses your file system (`.devhive/specs/`) as its database, generating readable Markdown files at each step of the software lifecycle.

## The Pipeline

DevHive is composed of specialized Agent Skills that work sequentially:

1. **`devhive-explorer`**: Analyzes the request and writes `.devhive/specs/01-exploration.md`
2. **`devhive-proposal`**: Creates acceptance criteria in `02-proposal.md`
3. **`devhive-architect`**: Designs the system architecture in `03-architecture.md`
4. **`devhive-taskplanner`**: Breaks the architecture into actionable items in `04-tasks.md`
5. **`devhive-developer`**: Writes the actual code and checks off tasks in `04-tasks.md`
6. **`devhive-qa`**: Writes test cases and test plans in `05-qa-plan.md`
7. **`devhive-auditor`**: Performs a final check and writes `06-audit.md`

All of this is managed by the **`devhive-orchestrator`** skill.

## Installation

To use DevHive in your OpenCode environment, run the install script. It will copy the skills into your local OpenCode configuration folder (`~/.config/opencode/skills/`).

```bash
./install.sh
```

## Usage

In OpenCode, simply ask the orchestrator to build your feature:

```
> Use the devhive-orchestrator skill to build a script that converts CSV to JSON.
```

By default, the orchestrator will pause and ask for your approval after writing each specification file (e.g., after writing the architecture design). If you want it to run entirely autonomously without stopping, you can add the "continuous mode" flag to your prompt:

```
> Use the devhive-orchestrator skill to build a React landing page. Run in continuous mode with no pauses.
```

## Why SDD (Skill-Driven Development)?

- **Zero Setup**: No Python servers, no MCP configuration, no background processes.
- **Local Memory**: The entire state of the project is readable by humans in `.devhive/specs/`. You can edit `02-proposal.md` manually, and the Architect will adapt to your changes.
- **Modular**: Need a different architectural approach? You can just tweak the prompt inside `skills/devhive_architect/SKILL.md`.

## License

MIT License.
