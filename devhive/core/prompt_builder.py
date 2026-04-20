import json
from typing import Dict, Any


class PromptBuilder:
    """
    Centralized prompt generation for all agents.
    Extracts prompts from agent logic to enable manual LLM execution.
    """
    
    # Memory search capability note (for active local RAG)
    MEMORY_SEARCH_NOTE = """

CRITICAL: You are encouraged to actively use the `devhive_search_memory` tool to find specific information from previous pipeline stages (e.g. architecture decisions, requirements, implementation details) if the provided context is not enough. You can also use `devhive_get_recent_memories`."""

    @staticmethod
    def build_prompts(agent_role: str, context: Dict[str, Any], **kwargs) -> Dict[str, str]:
        if agent_role == "CEO":
            return PromptBuilder._build_ceo_prompts(context, **kwargs)
        elif agent_role == "Explorer":
            return PromptBuilder._build_explorer_prompts(context, **kwargs)
        elif agent_role == "Proposal":
            return PromptBuilder._build_proposal_prompts(context)
        elif agent_role == "Architect":
            return PromptBuilder._build_architect_prompts(context)
        elif agent_role == "TaskPlanner":
            return PromptBuilder._build_task_planner_prompts(context)
        elif agent_role == "Developer":
            return PromptBuilder._build_developer_prompts(context)
        elif agent_role == "QA":
            return PromptBuilder._build_qa_prompts(context)
        elif agent_role == "Auditor":
            return PromptBuilder._build_auditor_prompts(context)
        elif agent_role == "Archivist":
            return PromptBuilder._build_archivist_prompts(context)
        else:
            raise ValueError(f"Unknown agent role: {agent_role}")

    @staticmethod
    def _build_ceo_prompts(context: Dict[str, Any], **kwargs) -> Dict[str, str]:
        requirements = kwargs.get("requirements", "No requirements provided")
        
        system_prompt = """
You are an AI orchestration agent called "CEO".

Your job is to orchestrate an AI software development pipeline by selecting and ordering agents to fulfill a feature request.

Available agents:
- Explorer
- Proposal
- Architect
- TaskPlanner
- Developer
- QA
- Auditor
- Archivist

Pipeline rules:
- Explorer should normally run first
- Developer must run before Archivist
- Archivist must always be the final step
- Agents must appear only once
- The workflow must be logically ordered

Output rules:
- Return valid JSON only
- Follow the schema exactly

Schema:
{
  "workflow_plan": ["Explorer", ...],
  "reasoning": "string"
}
"""
        
        user_prompt = f"""
Feature request:

{requirements}

Determine the optimal sequence of agents to execute.
"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_explorer_prompts(context: Dict[str, Any], **kwargs) -> Dict[str, str]:
        requirements = kwargs.get("requirements", "No requirements provided")
        
        system_prompt = f"""
You are an AI software architecture analyst called "Analyst (Explorer)".
Your role is to explore the codebase and requirements, producing a structured technical analysis.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.
- Do not include explanations outside JSON.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["string"],
  "phase_data": {{
    "user_needs": "string",
    "constraints": ["string"],
    "dependencies": ["string"],
    "complexity": "low" | "medium" | "high",
    "suggested_workflow": "fast_track" | "standard" | "comprehensive",
    "new_guidelines_content": "string" | null,
    "clarification_question": "string" | null
  }}
}}
"""
        
        user_prompt = f"""
Analyze the following feature request: {requirements}

Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Understand the Request: Is it a feature, bug fix, or refactor?
2. Investigate Context: Identify potential dependencies or guidelines. Ask clarification if needed.
3. Analyze Complexity: Estimate as low, medium, or high.
4. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_proposal_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are the Product Manager.
Your role is to create a formal feature proposal based on exploration.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["string"],
  "phase_data": {{
    "feature_description": "string",
    "user_value": "string",
    "acceptance_criteria": ["string"],
    "scope": "string"
  }}
}}
"""
        user_prompt = f"""
Create a feature proposal based on the exploration phase.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Review Context: Read the exploration analysis.
2. Define Value: State why the user needs this.
3. Define Criteria: List 3-5 clear acceptance criteria.
4. Define Scope: Clearly mark what is IN and OUT of scope.
5. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_architect_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are the Tech Lead (Architect).
Your role is to design the technical architecture for the feature.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["string"],
  "phase_data": {{
    "architecture_pattern": "string",
    "components": ["string"],
    "data_models": ["string"],
    "apis": ["string"]
  }}
}}
"""
        user_prompt = f"""
Design the architecture for the feature.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Review Context: Read proposal and exploration phases.
2. System Design: Decide on the architecture pattern.
3. Component Breakdown: Identify new components or services.
4. Interface Design: Design data models and APIs.
5. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_task_planner_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are the Scrum Master (TaskPlanner).
Your role is to break down the architecture into actionable development tasks.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["string"],
  "phase_data": {{
    "epics": ["string"],
    "tasks": [
      {{ "name": "string", "description": "string" }}
    ],
    "estimated_complexity": "low" | "medium" | "high"
  }}
}}
"""
        user_prompt = f"""
Break down the feature into development tasks.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Review Context: Understand the architecture and acceptance criteria.
2. Define Epics: Create high-level buckets.
3. Extract Tasks: Write specific, actionable tasks for the developer.
4. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_developer_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are the Developer.
Your role is to write the implementation code based on the specifications.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["list of written file paths"],
  "phase_data": {{
    "implementation_strategy": "string",
    "file_structure": ["string"],
    "pseudocode": "string",
    "files": [
      {{ "path": "string", "content": "string" }}
    ]
  }}
}}
"""
        user_prompt = f"""
Implement the feature.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Review Plan: Read the tasks, architecture, and proposal.
2. Adhere to Guidelines: Check 'project_guidelines'.
3. Formulate Strategy: Decide how you'll write the code.
4. Write Code: Include ACTUAL code in the 'files' array.
5. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_qa_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are QA.
Your role is to write test cases and validate the implementation.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": ["list of written test file paths"],
  "phase_data": {{
    "test_strategy": "string",
    "unit_tests": ["string"],
    "validation_plan": "string",
    "files": [
      {{ "path": "string", "content": "string" }}
    ]
  }}
}}
"""
        user_prompt = f"""
Generate tests for the implementation.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Review Code: Check the Developer's output.
2. Create Strategy: Define how you'll test the new feature.
3. Write Tests: Output actual test code files.
4. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_auditor_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"""
You are the Auditor.
Your role is to verify project consistency, architecture, and security.{PromptBuilder.MEMORY_SEARCH_NOTE}

Output rules:
- Output valid JSON only with the EXACT envelope structure below.

ENVELOPE SCHEMA:
{{
  "status": "success" | "partial" | "blocked",
  "executive_summary": "string (1-3 sentences)",
  "risks": ["string"],
  "artifacts_produced": [],
  "phase_data": {{
    "architecture_consistency": true | false,
    "missing_pieces": ["string"],
    "security_risks": ["string"]
  }}
}}
"""
        user_prompt = f"""
Verify the project implementation.
Context: {json.dumps(context, default=str)}

WHAT TO DO (PLAYBOOK):
1. Complete Audit: Verify if the implementation matches the proposal/architecture.
2. Security Check: Search for potential vulnerabilities.
3. Gap Analysis: Find any missing tasks.
4. Prepare Envelope: Return your findings in the strict JSON envelope.
"""
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _build_archivist_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        return {
            "system_prompt": "You are the Archivist. No LLM needed.",
            "user_prompt": "Archivist automatically archives the project. No user input required."
        }

