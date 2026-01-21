"""
Pydantic schemas for structured outputs from AI agents.
Using structured outputs ensures type safety and validation.
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class BlueprintComponent(BaseModel):
    """A single component in the blueprint"""
    name: str = Field(description="Component name (e.g., 'FeedbackForm')")
    type: Literal["frontend", "backend", "database"] = Field(description="Component type")
    file_path: str = Field(description="Where this file should be created")
    dependencies: List[str] = Field(default_factory=list, description="Other components this depends on")
    description: str = Field(description="What this component does")


class APIEndpoint(BaseModel):
    """Definition of a backend API endpoint"""
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    path: str = Field(description="API route path (e.g., '/api/feedback')")
    description: str
    request_body: Optional[Dict] = Field(default=None, description="Expected request body schema")
    response_body: Optional[Dict] = Field(default=None, description="Response schema")
    auth_required: bool = Field(default=True)


class FirestoreCollection(BaseModel):
    """Firestore collection schema"""
    name: str = Field(description="Collection name")
    document_schema: Dict[str, str] = Field(description="Document field types")
    indexes: List[str] = Field(default_factory=list, description="Fields to index")


class Blueprint(BaseModel):
    """Complete technical blueprint for a feature"""
    feature_name: str = Field(description="Name of the feature being built")
    description: str = Field(description="High-level description")

    # Components
    components: List[BlueprintComponent] = Field(description="All code components needed")
    api_endpoints: List[APIEndpoint] = Field(default_factory=list)
    firestore_collections: List[FirestoreCollection] = Field(default_factory=list)

    # Estimates
    complexity: Literal["simple", "medium", "complex"] = Field(description="Overall complexity")
    estimated_lines_of_code: int = Field(description="Rough LOC estimate")
    estimated_tokens: int = Field(description="Estimated tokens to generate code")

    # Tech stack
    frontend_tech: List[str] = Field(default_factory=lambda: ["Next.js", "TypeScript", "Tailwind"])
    backend_tech: List[str] = Field(default_factory=lambda: ["FastAPI", "Python"])
    database_tech: str = Field(default="Cloud Firestore")


class TestCase(BaseModel):
    """A single E2E test case"""
    name: str = Field(description="Test case name")
    description: str = Field(description="What this test validates")
    test_code: str = Field(description="Playwright test code")


class TestSuite(BaseModel):
    """Complete test suite for the feature"""
    file_name: str = Field(description="Test file name (e.g., 'feedback.spec.ts')")
    setup_code: Optional[str] = Field(default=None, description="Setup/teardown code")
    test_cases: List[TestCase] = Field(description="Individual test cases")
    mocked_api_responses: Dict[str, Dict] = Field(
        default_factory=dict,
        description="API routes to mock and their responses"
    )


class CodeFile(BaseModel):
    """A single code file to be generated"""
    file_path: str = Field(description="Full path where file should be saved")
    file_type: Literal["typescript", "python", "css", "config"] = Field(description="File type")
    content: str = Field(description="Complete file content")
    description: str = Field(description="What this file does")


class Implementation(BaseModel):
    """Complete implementation of the feature"""
    files: List[CodeFile] = Field(description="All files to create/modify")
    setup_instructions: List[str] = Field(description="Steps to set up the feature")
    testing_notes: str = Field(description="How to test this feature")


class SandboxResult(BaseModel):
    """Results from sandbox test execution"""
    passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_messages: List[str] = Field(default_factory=list)
    execution_time_ms: float
    logs: str = Field(description="Full test output logs")
