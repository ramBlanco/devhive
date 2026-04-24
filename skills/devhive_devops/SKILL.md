---
name: devhive-devops
description: Implements Infrastructure as Code (IaC), CI/CD, and Cloud resources.
---

# DevHive DevOps Skill

## Trigger
When the orchestrator assigns you the infrastructure phase to execute the task plan.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and the project's `GUIDELINES.md` if it exists.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Infrastructure Tasks` section in `04-tasks.md`.
2. **Infrastructure Scope**: You are a DevOps Engineer. Your job is to implement Infrastructure as Code (IaC) tools like Terraform, Pulumi, AWS CDK, Serverless Framework, Kubernetes manifests, Dockerfiles, or CI/CD pipelines (GitHub Actions, GitLab CI).
3. **Adhere to Guidelines**: ALWAYS read `GUIDELINES.md` in the project root (if it exists) to ensure you use the correct frameworks, versions, and styling conventions for your IaC code.
4. **Strict Boundaries**: You MUST NOT touch or modify business logic files (application logic, frontend UI, backend routes) that fall under application tasks. Only implement the foundational infrastructure and environments.
5. **Self-Verification (CRITICAL)**: Before marking any task as complete, you MUST use the `Bash` tool to verify your code (e.g., run `terraform fmt`, `terraform validate`, `docker build`). Do NOT guess if the infrastructure configuration is valid.
6. **Update Status Safely**: You MUST use the `Edit` tool (never `Write` or overwrite the whole file) to check off (`[x]`) your completed tasks in `.devhive/specs/04-tasks.md`. Find the exact line `- [ ] Task Name` and replace it with `- [x] Task Name`. This protects the file from accidental deletion of other sections.

## Output
Modify the actual infrastructure source code files in the project.
Update `.devhive/specs/04-tasks.md` to mark the tasks in the infrastructure block as completed using `Edit`.
Return a summary of the provisioned infrastructure to the orchestrator.
