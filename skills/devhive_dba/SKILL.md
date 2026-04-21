---
name: devhive-dba
description: Designs schemas, applies database migrations, writes queries, and manages data seeders.
---

# DevHive Database Administrator (DBA) Skill

## Trigger
When the orchestrator assigns you the data phase to execute the task plan.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md` (which should contain the data models), and the project's `GUIDELINES.md` if it exists.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills, and ALWAYS load your hardcoded skills: `db-optimization-expert`.
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Data Tasks` section in `04-tasks.md`. Ignore any other sections.
2. **Database Scope**: You are responsible for creating database schemas, running migrations, creating seeders, optimizing queries, adding indexes, and managing data constraints based on the `03-architecture.md` definitions. Assume the raw infrastructure (the DB server/cloud instance) has been provisioned by DevOps. You are managing the schema *inside* the DB.
3. **Adhere to Guidelines**: ALWAYS read `GUIDELINES.md` in the project root (if it exists) to ensure you use the correct ORM (Prisma, TypeORM, Diesel, SQLAlchemy, etc.) and database technology.
4. **Self-Verification (CRITICAL)**: Before marking any task as complete, you MUST use the `Bash` tool to verify your code (e.g., run `npx prisma format`, `npx prisma validate`, `alembic check`, `cargo check`). Do NOT guess if the migrations are valid. Run the migration if you can.
5. **Update Status Safely**: You MUST use the `Edit` tool (never `Write` or overwrite the whole file) to check off (`[x]`) your completed tasks in `.devhive/specs/04-tasks.md`. Find the exact line `- [ ] Task Name` and replace it with `- [x] Task Name`. This protects the file from accidental deletion of other sections.

## Output
Modify the actual data migration, seeder, and schema source code files in the project (e.g., `schema.prisma`, `migrations/*`, `seed.js`).
Update `.devhive/specs/04-tasks.md` to mark the tasks in the data block as completed using `Edit`.
Return a summary of the implemented database changes to the orchestrator.