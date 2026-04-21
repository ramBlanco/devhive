---
name: devhive-sast
description: Performs Static Application Security Testing (SAST) on the implemented code and infrastructure.
---

# DevHive SAST Skill

## Trigger
When the orchestrator assigns you the security audit phase after development is complete, before QA.

## Input Context
Read all implemented application code and infrastructure files (e.g., Dockerfiles, Terraform). Read `.devhive/specs/03-architecture.md` to understand the intended design.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills, and ALWAYS load your hardcoded skills: `owasp-top-10-auditor`, `secure-code-reviewer`. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Review Implementation**: Scan the code changes made by the Developer and DevOps agents.
2. **Security Scan**: Actively look for vulnerabilities such as SQL/NoSQL injections, XSS, hardcoded secrets, weak cryptographic libraries, exposed ports, and overly permissive IAM roles.
3. **Informative Mode**: Document all your findings categorized by severity (Critical, High, Medium, Low). Do not modify the code or uncheck tasks in `04-tasks.md`. Your goal is to provide visibility.
4. **Generate Report**: Create a detailed SAST report.

## Output
You MUST use the `Write` tool to save your security report to `.devhive/specs/05-sast-report.md`.

The markdown file should be structured as follows:

```markdown
# Phase 05: SAST Report

## Executive Summary
[1-3 sentences summarizing the security posture]

## Vulnerabilities Found
### Critical
- [Description and location, or "None"]

### High
- [Description and location, or "None"]

### Medium / Low
- [Description and location, or "None"]

## Recommendations
- [Actionable advice for fixing the issues]
```
