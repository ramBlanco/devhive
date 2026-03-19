from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalysisSchema(BaseModel):
    problem_summary: str = Field(..., description="Summary of the core problem")
    user_needs: List[str] = Field(..., description="Key user requirements")
    constraints: List[str] = Field(..., description="Technical or business constraints")
    dependencies: List[str] = Field(..., description="External dependencies")
    risks: List[str] = Field(..., description="Potential risks and mitigation strategies")

class ProposalSchema(BaseModel):
    feature_description: str = Field(..., description="Detailed description of the feature")
    user_value: str = Field(..., description="Value proposition for the user")
    acceptance_criteria: List[str] = Field(..., description="Conditions for success")
    scope: str = Field(..., description="Defined scope of the feature")
    non_goals: List[str] = Field(..., description="Explicitly out-of-scope items")

class ArchitectureSchema(BaseModel):
    architecture_pattern: str = Field(..., description="Chosen architectural pattern")
    components: List[str] = Field(..., description="Key system components")
    data_models: List[Dict[str, Any]] = Field(..., description="Data structures and schemas")
    apis: List[str] = Field(..., description="API endpoints and signatures")
    dependencies: List[str] = Field(..., description="Libraries and frameworks")

class TaskSchema(BaseModel):
    epics: List[str] = Field(..., description="High-level epics")
    tasks: List[Dict[str, Any]] = Field(..., description="Breakdown of tasks with estimates")
    subtasks: List[str] = Field(..., description="Detailed subtasks")
    estimated_complexity: str = Field(..., description="Complexity rating (Low/Medium/High)")

class ImplementationSchema(BaseModel):
    implementation_strategy: str = Field(..., description="Approach to coding the solution")
    code_examples: List[str] = Field(..., description="Sample code snippets")
    file_structure: str = Field(..., description="Proposed file organization")
    pseudocode: str = Field(..., description="High-level logic flow")

class TestingSchema(BaseModel):
    test_strategy: str = Field(..., description="Overall testing approach")
    unit_tests: List[str] = Field(..., description="List of unit tests to implement")
    edge_cases: List[str] = Field(..., description="Edge cases to cover")
    validation_plan: str = Field(..., description="Validation steps")

class VerificationSchema(BaseModel):
    architecture_consistency: bool = Field(..., description="Does implementation match design?")
    missing_pieces: List[str] = Field(..., description="Identified gaps")
    security_risks: List[str] = Field(..., description="Security concerns")
    performance_risks: List[str] = Field(..., description="Performance bottlenecks")

class ArchiveSchema(BaseModel):
    project_summary: str = Field(..., description="Executive summary of the project")
    artifacts: Dict[str, Any] = Field(..., description="Collection of all generated artifacts")
