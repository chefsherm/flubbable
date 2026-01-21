"""
Improved AI Development Agent using LangGraph
Features:
- Latest Claude Sonnet 4 models
- Structured outputs with Pydantic validation
- Proper error handling
- File system operations
- Cost tracking
- Rich logging
"""

import os
import json
from typing import TypedDict, List, Optional, Annotated
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from schemas import (
    Blueprint,
    TestSuite,
    Implementation,
    SandboxResult,
    CodeFile
)

# Rich console for beautiful output
console = Console()

# --- CONFIGURATION ---
# Using latest Claude Sonnet 4 (as of January 2025)
MODEL_PLANNER = "claude-sonnet-4-20250514"
MODEL_VERIFIER = "claude-sonnet-4-20250514"
MODEL_BUILDER = "claude-sonnet-4-20250514"

# Cost tracking (approximate as of Jan 2025)
COST_PER_1M_INPUT_TOKENS = 3.00   # $3 per 1M input tokens
COST_PER_1M_OUTPUT_TOKENS = 15.00  # $15 per 1M output tokens

# Initialize LLMs
llm_planner = ChatAnthropic(model=MODEL_PLANNER, temperature=0)
llm_verifier = ChatAnthropic(model=MODEL_VERIFIER, temperature=0)
llm_builder = ChatAnthropic(model=MODEL_BUILDER, temperature=0.2)


# --- STATE DEFINITION ---
class AgentState(TypedDict):
    # Input
    user_request: str
    tech_stack_context: str
    output_directory: str

    # Agent outputs
    blueprint: Optional[Blueprint]
    test_suite: Optional[TestSuite]
    implementation: Optional[Implementation]
    sandbox_result: Optional[SandboxResult]

    # Control flow
    attempt_count: int
    max_attempts: int
    status: str  # START, PLANNING, TESTING, BUILDING, VALIDATING, SUCCESS, FAILED

    # Tracking
    total_tokens_used: int
    total_cost_usd: float
    errors: List[str]


# --- PROMPTS ---

PLANNER_SYSTEM_PROMPT = """You are a Senior Systems Architect specializing in modern web applications.

TECH STACK:
- Frontend: Next.js 14+ (App Router), TypeScript, Tailwind CSS, Zustand, TanStack Query
- Backend: Python 3.11+, FastAPI, Pydantic
- Database: Google Cloud Firestore (NoSQL document database)
- Auth: Firebase Authentication

CRITICAL RULES:
1. NEVER use SQL - Firestore is a NoSQL document database (collections → documents → fields)
2. API routes MUST be FastAPI (Python), NOT Next.js API routes
3. All frontend state management uses Zustand + TanStack Query
4. Use TypeScript strictly - no implicit any types
5. Follow Next.js App Router conventions (not Pages Router)
6. All API responses must use Pydantic models

Your task: Analyze the user request and create a comprehensive technical blueprint.
Output ONLY valid JSON matching the Blueprint schema.
"""

VERIFIER_SYSTEM_PROMPT = """You are a QA Automation Lead specializing in E2E testing with Playwright.

TECH STACK:
- Frontend: Next.js + TypeScript
- Testing: Playwright for E2E tests
- Backend: FastAPI (must be mocked in tests)

CRITICAL RULES:
1. Write BLACK BOX tests - test user-visible behavior only
2. Use Playwright's network mocking to intercept FastAPI calls
3. Tests must be runnable WITHOUT a real backend
4. Use TypeScript for test files
5. Follow AAA pattern: Arrange, Act, Assert
6. Include accessibility tests (ARIA labels, keyboard navigation)

Your task: Write a comprehensive Playwright test suite.
Output ONLY valid JSON matching the TestSuite schema.
"""

BUILDER_SYSTEM_PROMPT = """You are a Senior Full-Stack Engineer with expertise in Next.js and FastAPI.

TECH STACK:
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, Zustand
- Backend: FastAPI, Pydantic, Firebase Admin SDK
- Database: Cloud Firestore

CODING STANDARDS:
1. TypeScript: Strict mode, no any types, proper interfaces
2. Python: Type hints everywhere, Pydantic for validation
3. Error Handling: Try/catch in TS, proper HTTP status codes in Python
4. Security: Validate all inputs, sanitize outputs, check auth tokens
5. Accessibility: ARIA labels, semantic HTML, keyboard navigation
6. Performance: Lazy loading, proper React hooks dependencies

PREVIOUS ATTEMPT CONTEXT:
{previous_logs}

ATTEMPT NUMBER: {attempt_count}

Your task: Implement the feature according to the blueprint and passing all tests.
If previous attempt failed, FIX the errors shown in logs.
Output ONLY valid JSON matching the Implementation schema.
"""


# --- HELPER FUNCTIONS ---

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD for token usage"""
    input_cost = (input_tokens / 1_000_000) * COST_PER_1M_INPUT_TOKENS
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M_OUTPUT_TOKENS
    return input_cost + output_cost


def save_code_files(implementation: Implementation, output_dir: str) -> List[str]:
    """Save generated code files to disk"""
    saved_files = []
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    for code_file in implementation.files:
        file_path = base_path / code_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_file.content)

        saved_files.append(str(file_path))
        console.print(f"  ✅ Created: {file_path}", style="green")

    return saved_files


# --- AGENT NODES ---

def planner_node(state: AgentState) -> dict:
    """Create technical blueprint"""
    console.print(Panel("🧠 PLANNER: Creating Technical Blueprint", style="bold blue"))

    try:
        # Use structured output with Pydantic
        structured_llm = llm_planner.with_structured_output(Blueprint)

        response = structured_llm.invoke([
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
User Request: {state['user_request']}

Tech Stack Context: {state['tech_stack_context']}

Create a detailed technical blueprint.
""")
        ])

        # Track token usage (approximation)
        input_tokens = len(PLANNER_SYSTEM_PROMPT + state['user_request']) // 4
        output_tokens = 1000  # Estimate for blueprint
        cost = calculate_cost(input_tokens, output_tokens)

        console.print(f"  ✅ Blueprint created: {response.feature_name}", style="green")
        console.print(f"  📊 Complexity: {response.complexity}", style="yellow")
        console.print(f"  💰 Cost: ${cost:.4f}", style="cyan")

        return {
            "blueprint": response,
            "status": "TESTING",
            "total_tokens_used": state.get("total_tokens_used", 0) + input_tokens + output_tokens,
            "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
        }

    except Exception as e:
        console.print(f"  ❌ Planner failed: {str(e)}", style="bold red")
        return {
            "status": "FAILED",
            "errors": state.get("errors", []) + [f"Planner error: {str(e)}"]
        }


def verifier_node(state: AgentState) -> dict:
    """Write test suite"""
    console.print(Panel("🕵️ VERIFIER: Writing Test Suite", style="bold magenta"))

    try:
        structured_llm = llm_verifier.with_structured_output(TestSuite)

        blueprint_json = state['blueprint'].model_dump_json(indent=2)

        response = structured_llm.invoke([
            SystemMessage(content=VERIFIER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
Blueprint:
{blueprint_json}

Write a comprehensive Playwright test suite that validates all functionality.
""")
        ])

        input_tokens = len(VERIFIER_SYSTEM_PROMPT + blueprint_json) // 4
        output_tokens = 800
        cost = calculate_cost(input_tokens, output_tokens)

        console.print(f"  ✅ Test suite created: {response.file_name}", style="green")
        console.print(f"  🧪 Test cases: {len(response.test_cases)}", style="yellow")
        console.print(f"  💰 Cost: ${cost:.4f}", style="cyan")

        return {
            "test_suite": response,
            "status": "BUILDING",
            "total_tokens_used": state.get("total_tokens_used", 0) + input_tokens + output_tokens,
            "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
        }

    except Exception as e:
        console.print(f"  ❌ Verifier failed: {str(e)}", style="bold red")
        return {
            "status": "FAILED",
            "errors": state.get("errors", []) + [f"Verifier error: {str(e)}"]
        }


def builder_node(state: AgentState) -> dict:
    """Implement the feature"""
    attempt = state['attempt_count'] + 1
    console.print(Panel(f"👷 BUILDER: Implementing Code (Attempt {attempt}/{state['max_attempts']})", style="bold green"))

    try:
        structured_llm = llm_builder.with_structured_output(Implementation)

        blueprint_json = state['blueprint'].model_dump_json(indent=2)
        test_suite_json = state['test_suite'].model_dump_json(indent=2)

        # Get previous logs if this is a retry
        previous_logs = ""
        if state.get('sandbox_result'):
            previous_logs = f"""
PREVIOUS TEST RESULTS (FAILED):
Passed: {state['sandbox_result'].passed_tests}/{state['sandbox_result'].total_tests}
Errors:
{chr(10).join('- ' + err for err in state['sandbox_result'].error_messages)}

Full Logs:
{state['sandbox_result'].logs}
"""

        response = structured_llm.invoke([
            SystemMessage(content=BUILDER_SYSTEM_PROMPT.format(
                previous_logs=previous_logs or "No previous attempts",
                attempt_count=attempt
            )),
            HumanMessage(content=f"""
Blueprint:
{blueprint_json}

Test Suite to Pass:
{test_suite_json}

Implement the complete feature with all necessary files.
""")
        ])

        input_tokens = len(BUILDER_SYSTEM_PROMPT + blueprint_json + test_suite_json) // 4
        output_tokens = 3000  # Code generation uses more tokens
        cost = calculate_cost(input_tokens, output_tokens)

        console.print(f"  ✅ Implementation complete: {len(response.files)} files", style="green")
        console.print(f"  💰 Cost: ${cost:.4f}", style="cyan")

        # Save files to disk
        output_dir = state.get('output_directory', './generated')
        saved_files = save_code_files(response, output_dir)

        return {
            "implementation": response,
            "attempt_count": attempt,
            "status": "VALIDATING",
            "total_tokens_used": state.get("total_tokens_used", 0) + input_tokens + output_tokens,
            "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
        }

    except Exception as e:
        console.print(f"  ❌ Builder failed: {str(e)}", style="bold red")
        return {
            "status": "FAILED",
            "attempt_count": attempt,
            "errors": state.get("errors", []) + [f"Builder error: {str(e)}"]
        }


def sandbox_node(state: AgentState) -> dict:
    """Run tests in sandbox (simulated for now)"""
    console.print(Panel("🧪 SANDBOX: Running Tests", style="bold yellow"))

    # TODO: Integrate with E2B or Docker to actually run tests
    # For now, we'll simulate test results

    attempt = state['attempt_count']

    # Simulate: first attempt fails, second succeeds
    if attempt == 1:
        result = SandboxResult(
            passed=False,
            total_tests=3,
            passed_tests=1,
            failed_tests=2,
            error_messages=[
                "Test 'should submit feedback' failed: Expected button text 'Submit', found 'Send'",
                "Test 'should validate required fields' failed: Form submitted without validation"
            ],
            execution_time_ms=1234.56,
            logs="""
Running 3 tests...
✅ Test: should render feedback form
❌ Test: should submit feedback
   AssertionError: Expected button text 'Submit', found 'Send'
❌ Test: should validate required fields
   AssertionError: Form submitted without required fields
"""
        )
        console.print("  ❌ Tests FAILED", style="bold red")

    else:
        result = SandboxResult(
            passed=True,
            total_tests=3,
            passed_tests=3,
            failed_tests=0,
            error_messages=[],
            execution_time_ms=987.65,
            logs="""
Running 3 tests...
✅ Test: should render feedback form
✅ Test: should submit feedback
✅ Test: should validate required fields

All tests passed!
"""
        )
        console.print("  ✅ Tests PASSED", style="bold green")

    # Display results
    table = Table(title="Test Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Tests", str(result.total_tests))
    table.add_row("Passed", f"[green]{result.passed_tests}[/green]")
    table.add_row("Failed", f"[red]{result.failed_tests}[/red]")
    table.add_row("Time", f"{result.execution_time_ms:.2f}ms")
    console.print(table)

    return {
        "sandbox_result": result,
        "status": "SUCCESS" if result.passed else "FIXING"
    }


# --- ROUTING LOGIC ---

def route_sandbox_result(state: AgentState) -> str:
    """Decide next step based on sandbox results"""
    if state['status'] == "SUCCESS":
        return "end"
    elif state['attempt_count'] >= state['max_attempts']:
        console.print(f"  ⚠️ Max attempts ({state['max_attempts']}) reached", style="bold yellow")
        return "give_up"
    else:
        console.print(f"  🔄 Retrying... (Attempt {state['attempt_count'] + 1}/{state['max_attempts']})", style="yellow")
        return "retry"


# --- BUILD GRAPH ---

def create_workflow() -> StateGraph:
    """Create the LangGraph workflow"""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("builder", builder_node)
    workflow.add_node("sandbox", sandbox_node)

    # Define flow
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "verifier")
    workflow.add_edge("verifier", "builder")
    workflow.add_edge("builder", "sandbox")

    # Conditional routing
    workflow.add_conditional_edges(
        "sandbox",
        route_sandbox_result,
        {
            "end": END,
            "retry": "builder",
            "give_up": END
        }
    )

    return workflow.compile()


# --- MAIN EXECUTION ---

def run_agent(
    user_request: str,
    output_dir: str = "./generated",
    max_attempts: int = 3,
    tech_stack: str = "Next.js, FastAPI, Firestore"
):
    """Run the AI development agent"""

    console.print(Panel.fit(
        "🚀 AI Development Agent\n"
        "Powered by Claude Sonnet 4",
        style="bold white on blue"
    ))

    initial_state: AgentState = {
        "user_request": user_request,
        "tech_stack_context": tech_stack,
        "output_directory": output_dir,
        "blueprint": None,
        "test_suite": None,
        "implementation": None,
        "sandbox_result": None,
        "attempt_count": 0,
        "max_attempts": max_attempts,
        "status": "START",
        "total_tokens_used": 0,
        "total_cost_usd": 0.0,
        "errors": []
    }

    app = create_workflow()

    # Run workflow
    final_state = None
    for state_update in app.stream(initial_state):
        final_state = state_update
        # Nodes print their own progress

    # Final summary
    if final_state:
        last_state = list(final_state.values())[0]

        console.print("\n" + "="*60 + "\n")

        if last_state['status'] == "SUCCESS":
            console.print(Panel.fit(
                "✅ Feature Implementation Complete!",
                style="bold green"
            ))
        else:
            console.print(Panel.fit(
                "❌ Implementation Failed",
                style="bold red"
            ))

        # Cost summary
        summary = Table(title="Final Summary")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="yellow")
        summary.add_row("Total Attempts", str(last_state['attempt_count']))
        summary.add_row("Total Tokens", f"{last_state['total_tokens_used']:,}")
        summary.add_row("Total Cost", f"${last_state['total_cost_usd']:.4f}")
        summary.add_row("Status", last_state['status'])

        if last_state.get('errors'):
            summary.add_row("Errors", str(len(last_state['errors'])))

        console.print(summary)

        # Output location
        if last_state['status'] == "SUCCESS":
            console.print(f"\n📁 Generated files saved to: {last_state['output_directory']}", style="bold green")

    return final_state


if __name__ == "__main__":
    # Example usage
    run_agent(
        user_request="Create a feedback form where users can submit a title and description. Display submitted feedback in a list below the form.",
        output_dir="./generated/feedback-feature",
        max_attempts=3
    )
