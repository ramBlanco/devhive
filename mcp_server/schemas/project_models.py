from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

# --- Sub-Schemas for each Phase ---

class AnalysisContent(BaseModel):
    user_needs: List[str] = Field(..., description="Key user requirements")
    constraints: List[str] = Field(..., description="Technical or business constraints")
    dependencies: List[str] = Field(..., description="External dependencies")
    risks: List[str] = Field(..., description="Potential risks and mitigation strategies")

class ProposalContent(BaseModel):
    feature_description: str = Field(..., description="Detailed description of the feature")
    user_value: str = Field(..., description="Value proposition for the user")
    acceptance_criteria: List[str] = Field(..., description="Conditions for success")
    scope: str = Field(..., description="Defined scope of the feature")

class ArchitectureContent(BaseModel):
    architecture_pattern: str = Field(..., description="Chosen architectural pattern")
    components: List[str] = Field(..., description="Key system components")
    data_models: List[Dict[str, Any]] = Field(..., description="Data structures and schemas")
    apis: List[str] = Field(..., description="API endpoints and signatures")

class TaskContent(BaseModel):
    epics: List[str] = Field(..., description="High-level epics")
    tasks: List[Dict[str, Any]] = Field(..., description="Breakdown of tasks with estimates")
    estimated_complexity: str = Field(..., description="Complexity rating (Low/Medium/High)")

class FileContent(BaseModel):
    path: str = Field(..., description="Relative path to the file")
    content: str = Field(..., description="Content of the file")

class ImplementationContent(BaseModel):
    implementation_strategy: str = Field(..., description="Approach to coding the solution")
    file_structure: str = Field(..., description="Proposed file organization")
    pseudocode: str = Field(..., description="High-level logic flow")
    files: List[FileContent] = Field(default_factory=list, description="Generated source code files")

class TestingContent(BaseModel):
    test_strategy: str = Field(..., description="Overall testing approach")
    unit_tests: List[str] = Field(..., description="List of unit tests to implement")
    validation_plan: str = Field(..., description="Validation steps")
    files: List[FileContent] = Field(default_factory=list, description="Generated test files")

class VerificationContent(BaseModel):
    architecture_consistency: bool = Field(..., description="Does implementation match design?")
    missing_pieces: List[str] = Field(..., description="Identified gaps")
    security_risks: List[str] = Field(..., description="Security concerns")

class ArchiveContent(BaseModel):
    project_summary: str = Field(..., description="Executive summary of the project")
    artifacts: Dict[str, Any] = Field(..., description="Collection of all generated artifacts")

class HistoryEntry(BaseModel):
    role: str
    action: str
    summary: str
    timestamp: float

# --- Main Project State ---

class ProjectState(BaseModel):
    feature_request: str
    analysis: Optional[AnalysisContent] = None
    proposal: Optional[ProposalContent] = None
    architecture: Optional[ArchitectureContent] = None
    tasks: Optional[TaskContent] = None
    implementation: Optional[ImplementationContent] = None
    testing: Optional[TestingContent] = None
    verification: Optional[VerificationContent] = None
    archived: bool = False
    history: List[HistoryEntry] = []
    
    class Config:
        arbitrary_types_allowed = True
