import json
from typing import Dict, Any


class PromptBuilder:
    """
    Centralized prompt generation for all agents.
    Extracts prompts from agent logic to enable manual LLM execution.
    """
    
    # Memory search capability note (for hybrid RAG mode)
    MEMORY_SEARCH_NOTE = """

Note: You have access to the devhive_search_memory tool if you need to find specific information from previous pipeline stages. Use it to search for details like architecture decisions, requirements, or implementation specifics."""

    @staticmethod
    def build_prompts(agent_role: str, context: Dict[str, Any], **kwargs) -> Dict[str, str]:
        """
        Build system and user prompts for a given agent.
        
        Args:
            agent_role: Name of the agent (Explorer, Proposal, etc.)
            context: Context dictionary from ContextRouter
            **kwargs: Additional parameters (e.g., requirements for Explorer)
        
        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys
        """
        
        if agent_role == "Explorer":
            return PromptBuilder._build_explorer_prompts(context, **kwargs)
        elif agent_role == "Proposal":
            return PromptBuilder._build_proposal_prompts(context)
        elif agent_role == "Architect":
            return PromptBuilder._build_architect_prompts(context)
        elif agent_role == "TaskPlanner":
            return PromptBuilder._build_task_planner_prompts(context)
        elif agent_role == "Developer":
            return PromptBuilder._build_developer_prompts(context)
        elif agent_role == "TaskDistributor":
            return PromptBuilder._build_task_distributor_prompts(context)
        elif agent_role == "QA":
            return PromptBuilder._build_qa_prompts(context)
        elif agent_role == "Auditor":
            return PromptBuilder._build_auditor_prompts(context)
        elif agent_role == "Archivist":
            return PromptBuilder._build_archivist_prompts(context)
        else:
            raise ValueError(f"Unknown agent role: {agent_role}")

    @staticmethod
    def _build_explorer_prompts(context: Dict[str, Any], **kwargs) -> Dict[str, str]:
        requirements = kwargs.get("requirements", "No requirements provided")
        
        system_prompt = "You are the Analyst (Explorer). Output JSON only."
        
        user_prompt = f"""Analyze the following feature request: {requirements}

Context: {json.dumps(context, default=str)}

Your task is to perform initial analysis and exploration.
Check 'project_guidelines' in the context. 
- If it says "Guidelines not found.", you MUST establish the technology stack.
  - If the stack is clear from the request (e.g. "Use Python/Flask"), generate a Markdown string for 'new_guidelines_content'.
  - If the stack is unclear, providing a question in 'clarification_question'.

Return JSON with the following keys:
- user_needs: String describing what users need from this feature
- constraints: List of technical or business constraints
- dependencies: List of external dependencies or requirements
- risks: List of potential risks or challenges
- complexity: "low", "medium", or "high". 
  - "low": Simple changes, no architecture needed.
  - "medium": Moderate changes, needs proposal but no complex architecture.
  - "high": Complex changes, needs full architecture and planning.
- suggested_workflow: "fast_track" (low), "standard" (medium), or "comprehensive" (high)
- new_guidelines_content: (Optional) Markdown string with best practices if guidelines were missing.
- clarification_question: (Optional) Question to ask user if tech stack is unclear.

Example format:
{{
  "user_needs": "Users need to export data in CSV format for analysis",
  "constraints": ["Must work with existing authentication", "Limited to 10MB file size"],
  "dependencies": ["CSV library", "File storage system"],
  "risks": ["Large datasets may cause performance issues", "Security concerns with file downloads"],
  "complexity": "medium",
  "suggested_workflow": "standard"
}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_proposal_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = "You are the Product Manager. Output JSON only."
        
        user_prompt = f"""Create a feature proposal based on the exploration phase.

Context: {json.dumps(context, default=str)}

Your task is to define the feature proposal with clear acceptance criteria.

Return JSON with the following keys:
- feature_description: Detailed description of the feature
- user_value: The value this feature provides to users
- acceptance_criteria: List of criteria that must be met
- scope: What is in and out of scope

Example format:
{{
  "feature_description": "Add CSV export functionality to analytics dashboard",
  "user_value": "Users can download and analyze data in Excel/spreadsheet tools",
  "acceptance_criteria": ["Export button visible on dashboard", "CSV file downloads successfully", "All visible data included in export"],
  "scope": "In scope: Basic CSV export. Out of scope: Excel formatting, scheduled exports"
}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_architect_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = "You are the Tech Lead. Output JSON only."
        
        user_prompt = f"""Design the architecture for the feature.

Context: {json.dumps(context, default=str)}

Your task is to create a technical architecture design.

Return JSON with the following keys:
- architecture_pattern: The architectural pattern to use (e.g., MVC, microservices)
- components: List of components/modules needed
- data_models: List of data models or database schemas
- apis: List of APIs or interfaces needed

Example format:
{{
  "architecture_pattern": "MVC with service layer",
  "components": ["ExportController", "CSVGeneratorService", "DataFetcherService"],
  "data_models": ["ExportJob", "ExportHistory"],
  "apis": ["POST /api/export/csv", "GET /api/export/status/:id"]
}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_task_planner_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = "You are the Scrum Master. Output JSON only."
        
        user_prompt = f"""Break down the feature into development tasks.

Context: {json.dumps(context, default=str)}

Your task is to create a task breakdown with estimates.

Return JSON with the following keys:
- epics: List of high-level epics
- tasks: List of task objects with name and description
- estimated_complexity: Overall complexity estimate (low/medium/high)

Example format:
{{
  "epics": ["Backend CSV generation", "Frontend export UI", "Testing"],
  "tasks": [
    {{"name": "Create CSVGeneratorService", "description": "Service to convert data to CSV format"}},
    {{"name": "Add export button to dashboard", "description": "UI component for triggering export"}}
  ],
  "estimated_complexity": "medium"
}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_developer_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"You are the Developer. Output JSON only.{PromptBuilder.MEMORY_SEARCH_NOTE}"
        
        user_prompt = f"""Implement the feature based on available specifications (requirements, proposal, or architecture).

Context: {json.dumps(context, default=str)}

Your task is to create the implementation plan and code.
CRITICAL: Check 'project_guidelines' in the context. You MUST strictly adhere to these best practices, naming conventions, and technology choices.

Return JSON with the following keys:
- implementation_strategy: High-level strategy for implementation
- file_structure: List of files that will be created/modified
- pseudocode: Brief pseudocode or implementation notes
- files: List of file objects with 'path' and 'content' keys

Example format:
{{
  "implementation_strategy": "Create service layer for CSV generation, add controller endpoint, add UI button",
  "file_structure": ["src/services/csv_generator.py", "src/controllers/export_controller.py"],
  "pseudocode": "1. Fetch data from database\\n2. Convert to CSV format\\n3. Return file response",
  "files": [
    {{
      "path": "src/services/csv_generator.py",
      "content": "class CSVGenerator:\\n    def generate(self, data):\\n        # Implementation here\\n        pass"
    }}
  ]
}}

IMPORTANT: Include actual code in the 'files' array. Each file should have 'path' and 'content' keys."""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_task_distributor_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = "You are the Task Distributor. You coordinate parallel development. Output JSON only."
        
        user_prompt = f"""Coordinate parallel development of tasks.

Context: {json.dumps(context, default=str)}

Your role is to execute the TaskDistributor workflow, which:
1. Loads tasks from TaskPlanner
2. Analyzes dependencies
3. Spawns developer agents for parallel execution
4. Aggregates results

This is handled automatically by the TaskDistributor agent.
No LLM response needed - this is a programmatic workflow.

Return empty JSON: {{}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_qa_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = f"You are QA. Output JSON only.{PromptBuilder.MEMORY_SEARCH_NOTE}"
        
        user_prompt = f"""Generate tests for the implementation.

Context: {json.dumps(context, default=str)}

Your task is to create a comprehensive test plan and test files.

Return JSON with the following keys:
- test_strategy: Overall testing strategy
- unit_tests: List of unit tests to implement
- validation_plan: How to validate the feature works
- files: List of test file objects with 'path' and 'content' keys

Example format:
{{
  "test_strategy": "Unit tests for service layer, integration tests for API endpoints",
  "unit_tests": ["test_csv_generation", "test_export_endpoint", "test_file_download"],
  "validation_plan": "Verify CSV file downloads correctly and contains expected data",
  "files": [
    {{
      "path": "tests/test_csv_generator.py",
      "content": "import unittest\\n\\nclass TestCSVGenerator(unittest.TestCase):\\n    def test_generate(self):\\n        pass"
    }}
  ]
}}

IMPORTANT: Include actual test code in the 'files' array."""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_auditor_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        system_prompt = "You are the Auditor. Output JSON only."
        
        user_prompt = f"""Verify the project implementation.

Context: {json.dumps(context, default=str)}

Your task is to audit the entire project for consistency and completeness.

Return JSON with the following keys:
- architecture_consistency: Boolean, whether architecture is consistent
- missing_pieces: List of missing components or incomplete parts
- security_risks: List of potential security issues

Example format:
{{
  "architecture_consistency": true,
  "missing_pieces": ["Error handling for large files", "Rate limiting on export endpoint"],
  "security_risks": ["No validation of user permissions", "Potential path traversal in file export"]
}}"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

    @staticmethod
    def _build_archivist_prompts(context: Dict[str, Any]) -> Dict[str, str]:
        # Archivist doesn't need LLM, but return empty prompts for consistency
        return {
            "system_prompt": "You are the Archivist. No LLM needed.",
            "user_prompt": "Archivist automatically archives the project. No user input required."
        }
