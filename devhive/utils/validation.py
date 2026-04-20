from typing import Dict, Any, Tuple, List

class ResponseValidator:
    """
    Validates LLM responses for each agent.
    Ensures responses contain the standard Envelope and valid phase_data structures.
    """

    @staticmethod
    def _validate_envelope(response: Dict[str, Any], agent_name: str) -> Tuple[bool, str]:
        """Validate the standard envelope structure used by all agents except CEO/Archivist."""
        if not isinstance(response, dict):
            return False, f"{agent_name}: Response must be a JSON object"
            
        envelope_keys = ["status", "executive_summary", "risks", "artifacts_produced", "phase_data"]
        missing = [k for k in envelope_keys if k not in response]
        
        if missing:
            return False, f"{agent_name}: Missing envelope keys: {', '.join(missing)}"
            
        if response["status"] not in ["success", "partial", "blocked"]:
            return False, f"{agent_name}: 'status' must be one of: success, partial, blocked"
            
        if not isinstance(response["phase_data"], dict):
            return False, f"{agent_name}: 'phase_data' must be an object"
            
        return True, ""

    @staticmethod
    def validate_ceo(response: Dict[str, Any]) -> Tuple[bool, str]:
        """CEO uses a custom structure, not the standard envelope."""
        required_keys = ["workflow_plan", "reasoning"]
        is_valid, error = ResponseValidator._validate_keys(response, required_keys, "CEO")
        if not is_valid:
            return is_valid, error
            
        if not isinstance(response.get("workflow_plan"), list):
            return False, "CEO: 'workflow_plan' must be a list of agent names"
            
        valid_agents = ["Explorer", "Proposal", "Architect", "TaskPlanner", "Developer", "QA", "Auditor", "Archivist"]
        for agent in response["workflow_plan"]:
            if agent not in valid_agents:
                return False, f"CEO: Invalid agent name '{agent}'"
                
        return True, ""

    @staticmethod
    def validate_explorer(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "Explorer")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["user_needs", "constraints", "dependencies", "complexity", "suggested_workflow"]
        return ResponseValidator._validate_keys(phase_data, required_keys, "Explorer phase_data")

    @staticmethod
    def validate_proposal(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "Proposal")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["feature_description", "user_value", "acceptance_criteria", "scope"]
        return ResponseValidator._validate_keys(phase_data, required_keys, "Proposal phase_data")

    @staticmethod
    def validate_architect(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "Architect")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["architecture_pattern", "components", "data_models", "apis"]
        return ResponseValidator._validate_keys(phase_data, required_keys, "Architect phase_data")

    @staticmethod
    def validate_task_planner(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "TaskPlanner")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["epics", "tasks", "estimated_complexity"]
        is_valid, error_msg = ResponseValidator._validate_keys(phase_data, required_keys, "TaskPlanner phase_data")
        if not is_valid: return False, error_msg
        
        if not isinstance(phase_data.get("tasks"), list):
            return False, "TaskPlanner phase_data: 'tasks' must be a list"
            
        for idx, task in enumerate(phase_data.get("tasks", [])):
            if not isinstance(task, dict):
                return False, f"TaskPlanner phase_data: Task at {idx} must be a dict"
            if "name" not in task or "description" not in task:
                return False, f"TaskPlanner phase_data: Task at {idx} missing 'name' or 'description'"
                
        return True, ""

    @staticmethod
    def validate_developer(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "Developer")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["implementation_strategy", "file_structure", "files"]
        is_valid, error_msg = ResponseValidator._validate_keys(phase_data, required_keys, "Developer phase_data")
        if not is_valid: return False, error_msg
        
        files = phase_data.get("files", [])
        if not isinstance(files, list):
            return False, "Developer phase_data: 'files' must be a list"
            
        for idx, f in enumerate(files):
            if not isinstance(f, dict) or "path" not in f or "content" not in f:
                return False, f"Developer phase_data: File at {idx} missing 'path' or 'content'"
                
        return True, ""

    @staticmethod
    def validate_qa(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "QA")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["test_strategy", "unit_tests", "validation_plan", "files"]
        is_valid, error_msg = ResponseValidator._validate_keys(phase_data, required_keys, "QA phase_data")
        if not is_valid: return False, error_msg
        
        files = phase_data.get("files", [])
        if not isinstance(files, list):
            return False, "QA phase_data: 'files' must be a list"
            
        for idx, f in enumerate(files):
            if not isinstance(f, dict) or "path" not in f or "content" not in f:
                return False, f"QA phase_data: File at {idx} missing 'path' or 'content'"
                
        return True, ""

    @staticmethod
    def validate_auditor(response: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, error = ResponseValidator._validate_envelope(response, "Auditor")
        if not is_valid: return False, error
        
        phase_data = response["phase_data"]
        required_keys = ["architecture_consistency", "missing_pieces", "security_risks"]
        return ResponseValidator._validate_keys(phase_data, required_keys, "Auditor phase_data")

    @staticmethod
    def _validate_keys(response: Dict[str, Any], required_keys: List[str], agent_name: str) -> Tuple[bool, str]:
        if not isinstance(response, dict):
            return False, f"{agent_name}: Response must be a dict"
        missing_keys = [k for k in required_keys if k not in response]
        if missing_keys:
            return False, f"{agent_name}: Missing required keys: {', '.join(missing_keys)}"
        return True, ""

    @staticmethod
    def get_expected_keys(agent_role: str) -> List[str]:
        envelope = ["status", "executive_summary", "risks", "artifacts_produced", "phase_data"]
        key_mapping = {
            "CEO": ["workflow_plan", "reasoning"],
            "Explorer": envelope,
            "Proposal": envelope,
            "Architect": envelope,
            "TaskPlanner": envelope,
            "Developer": envelope,
            "QA": envelope,
            "Auditor": envelope,
            "Archivist": []
        }
        return key_mapping.get(agent_role, [])
