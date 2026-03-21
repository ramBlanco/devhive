from typing import Dict, Any, Tuple, List


class ResponseValidator:
    """
    Validates LLM responses for each agent.
    Ensures responses contain required keys and valid data structures.
    """

    @staticmethod
    def validate_explorer(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Explorer agent response.
        
        Expected keys: user_needs, constraints, dependencies, risks, complexity, suggested_workflow
        Optional keys: new_guidelines_content, clarification_question
        """
        required_keys = ["user_needs", "constraints", "dependencies", "risks", "complexity", "suggested_workflow"]
        is_valid, error = ResponseValidator._validate_keys(response, required_keys, "Explorer")
        if not is_valid:
            return is_valid, error
            
        if "new_guidelines_content" in response and not isinstance(response["new_guidelines_content"], str):
             return False, "Explorer: 'new_guidelines_content' must be a string"
             
        if "clarification_question" in response and not isinstance(response["clarification_question"], str):
             return False, "Explorer: 'clarification_question' must be a string"
             
        return True, ""

    @staticmethod
    def validate_proposal(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Proposal agent response.
        
        Expected keys: feature_description, user_value, acceptance_criteria, scope
        """
        required_keys = ["feature_description", "user_value", "acceptance_criteria", "scope"]
        return ResponseValidator._validate_keys(response, required_keys, "Proposal")

    @staticmethod
    def validate_architect(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Architect agent response.
        
        Expected keys: architecture_pattern, components, data_models, apis
        """
        required_keys = ["architecture_pattern", "components", "data_models", "apis"]
        return ResponseValidator._validate_keys(response, required_keys, "Architect")

    @staticmethod
    def validate_task_planner(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate TaskPlanner agent response.
        
        Expected keys: epics, tasks, estimated_complexity
        """
        required_keys = ["epics", "tasks", "estimated_complexity"]
        is_valid, error_msg = ResponseValidator._validate_keys(response, required_keys, "TaskPlanner")
        
        if not is_valid:
            return is_valid, error_msg
        
        # Additional validation: tasks should be a list
        if not isinstance(response.get("tasks"), list):
            return False, "TaskPlanner: 'tasks' must be a list of task objects"
        
        return True, ""

    @staticmethod
    def validate_developer(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Developer agent response.
        
        Expected keys: implementation_strategy, file_structure, pseudocode, files
        """
        required_keys = ["implementation_strategy", "file_structure", "files"]
        is_valid, error_msg = ResponseValidator._validate_keys(response, required_keys, "Developer")
        
        if not is_valid:
            return is_valid, error_msg
        
        # Additional validation: files should be a list with path and content
        files = response.get("files", [])
        if not isinstance(files, list):
            return False, "Developer: 'files' must be a list of file objects"
        
        for idx, file_obj in enumerate(files):
            if not isinstance(file_obj, dict):
                return False, f"Developer: File at index {idx} must be a dict with 'path' and 'content'"
            if "path" not in file_obj or "content" not in file_obj:
                return False, f"Developer: File at index {idx} missing 'path' or 'content' keys"
        
        return True, ""

    @staticmethod
    def validate_qa(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate QA agent response.
        
        Expected keys: test_strategy, unit_tests, validation_plan, files
        """
        required_keys = ["test_strategy", "unit_tests", "validation_plan", "files"]
        is_valid, error_msg = ResponseValidator._validate_keys(response, required_keys, "QA")
        
        if not is_valid:
            return is_valid, error_msg
        
        # Additional validation: files should be a list with path and content
        files = response.get("files", [])
        if not isinstance(files, list):
            return False, "QA: 'files' must be a list of test file objects"
        
        for idx, file_obj in enumerate(files):
            if not isinstance(file_obj, dict):
                return False, f"QA: File at index {idx} must be a dict with 'path' and 'content'"
            if "path" not in file_obj or "content" not in file_obj:
                return False, f"QA: File at index {idx} missing 'path' or 'content' keys"
        
        return True, ""

    @staticmethod
    def validate_auditor(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate Auditor agent response.
        
        Expected keys: architecture_consistency, missing_pieces, security_risks
        """
        required_keys = ["architecture_consistency", "missing_pieces", "security_risks"]
        is_valid, error_msg = ResponseValidator._validate_keys(response, required_keys, "Auditor")
        
        if not is_valid:
            return is_valid, error_msg
        
        # Additional validation: architecture_consistency should be boolean
        if not isinstance(response.get("architecture_consistency"), bool):
            return False, "Auditor: 'architecture_consistency' must be a boolean (true/false)"
        
        return True, ""

    @staticmethod
    def _validate_keys(response: Dict[str, Any], required_keys: List[str], agent_name: str) -> Tuple[bool, str]:
        """
        Helper method to validate that all required keys exist in response.
        
        Args:
            response: The response dict to validate
            required_keys: List of required key names
            agent_name: Name of the agent (for error messages)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(response, dict):
            return False, f"{agent_name}: Response must be a JSON object/dict, got {type(response).__name__}"
        
        missing_keys = [key for key in required_keys if key not in response]
        
        if missing_keys:
            return False, f"{agent_name}: Missing required keys: {', '.join(missing_keys)}. Required keys are: {', '.join(required_keys)}"
        
        return True, ""

    @staticmethod
    def get_expected_keys(agent_role: str) -> List[str]:
        """
        Get the list of expected keys for a given agent role.
        Useful for error messages and documentation.
        
        Args:
            agent_role: The agent role name
        
        Returns:
            List of expected key names
        """
        key_mapping = {
            "Explorer": ["user_needs", "constraints", "dependencies", "risks", "complexity", "suggested_workflow", "new_guidelines_content", "clarification_question"],
            "Proposal": ["feature_description", "user_value", "acceptance_criteria", "scope"],
            "Architect": ["architecture_pattern", "components", "data_models", "apis"],
            "TaskPlanner": ["epics", "tasks", "estimated_complexity"],
            "Developer": ["implementation_strategy", "file_structure", "files"],
            "QA": ["test_strategy", "unit_tests", "validation_plan", "files"],
            "Auditor": ["architecture_consistency", "missing_pieces", "security_risks"],
            "Archivist": []  # No validation needed
        }
        
        return key_mapping.get(agent_role, [])
