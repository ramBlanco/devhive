---
name: devhive-devops
description: Implements Infrastructure as Code (IaC), CI/CD, and Cloud resources.
---

# DevHive DevOps Skill

## Trigger
When the orchestrator assigns you the infrastructure phase to execute the task plan.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and any existing project guidelines.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Infrastructure Tasks` section in `04-tasks.md`.
2. **Infrastructure Scope**: You are a DevOps Engineer. Your job is to implement Infrastructure as Code (IaC) tools like Terraform, Pulumi, AWS CDK, Serverless Framework, Kubernetes manifests, Dockerfiles, or CI/CD pipelines (GitHub Actions, GitLab CI).
3. **Strict Boundaries**: You MUST NOT touch or modify business logic files (application logic, frontend UI, backend routes) that fall under application tasks. Only implement the foundational infrastructure and environments.
4. **Implement**: Write or edit the configuration code to complete the infrastructure tasks using the `Write` and `Edit` tools.
5. **Update Status**: Update `.devhive/specs/04-tasks.md` to check off (`[x]`) the infrastructure tasks you have completed. You can use the `Edit` tool for this.

## Output
Modify the actual infrastructure source code files in the project.
Update `.devhive/specs/04-tasks.md` to mark the tasks in the infrastructure block as completed.
Return a summary of the provisioned infrastructure to the orchestrator.
