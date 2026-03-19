from typing import TypedDict, Dict, Any, List

class FeatureAnalysis(TypedDict):
    user_needs: List[str]
    constraints: List[str]
    risks: List[str]
    dependencies: List[str]
    required_components: List[str]

class ProductProposal(TypedDict):
    feature_description: str
    user_value: str
    acceptance_criteria: List[str]
    scope: str
    non_goals: List[str]

class ArchitectureDesign(TypedDict):
    architecture: str
    components: List[str]
    apis: List[str]
    data_structures: List[Dict[str, Any]]
    dependencies: List[str]

class TaskList(TypedDict):
    epics: List[str]
    tasks: List[Dict[str, Any]]
    subtasks: List[str]
    estimated_complexity: str

class ImplementationPlan(TypedDict):
    implementation_strategy: str
    code_examples: List[str]
    file_structure: str
    pseudocode: str

class TestingPlan(TypedDict):
    test_strategy: str
    unit_tests: List[str]
    edge_cases: List[str]
    validation_plan: str

class AuditReport(TypedDict):
    architecture_consistency: bool
    missing_pieces: List[str]
    security_risks: List[str]
    performance_risks: List[str]

class ArchiveRecord(TypedDict):
    summarized_documentation: str
    structured_artifact: Dict[str, Any]

class FeatureBuildResult(TypedDict):
    analysis: FeatureAnalysis
    proposal: ProductProposal
    architecture: ArchitectureDesign
    tasks: TaskList
    implementation: ImplementationPlan
    testing: TestingPlan
    verification: AuditReport
    archive: ArchiveRecord
