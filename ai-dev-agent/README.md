# AI Development Agent 🤖

A production-ready AI software engineering agent built with LangGraph and Claude Sonnet 4. This agent can plan, test, implement, and validate complete features using a test-driven development workflow.

## ✨ Features

- **🧠 Smart Planning** - Creates detailed technical blueprints with Claude Sonnet 4
- **🕵️ Test-First Approach** - Writes Playwright E2E tests before implementation
- **👷 Self-Correcting Builder** - Implements code and fixes errors automatically
- **🧪 Real Test Execution** - E2B cloud sandbox integration for actual Playwright tests
- **🎭 Simulation Mode** - Fast simulated testing for development/prototyping
- **💰 Cost Tracking** - Monitors token usage and API costs in real-time
- **📊 Structured Outputs** - Type-safe Pydantic schemas for all AI responses
- **🎨 Beautiful CLI** - Rich terminal UI with progress tracking
- **🔄 Retry Logic** - Automatically retries on failures up to max attempts
- **💾 File Generation** - Saves generated code directly to disk

## 🆕 Improvements Over Original

### ✅ Fixed Issues

| Issue | Solution |
|-------|----------|
| Outdated Claude 3.5 model | ✅ Updated to `claude-sonnet-4-20250514` |
| String JSON parsing | ✅ Structured outputs with Pydantic `.with_structured_output()` |
| No error handling | ✅ Try/catch blocks with detailed error tracking |
| Simulated sandbox only | ✅ **Full E2B integration - real Playwright tests!** |
| No file system ops | ✅ Generates and saves files to disk |
| No cost tracking | ✅ Real-time token usage and cost calculation |
| Poor logging | ✅ Rich terminal UI with tables and panels |

### 🚀 New Features

- **Structured Schemas**: Type-safe `Blueprint`, `TestSuite`, `Implementation` models
- **Cost Estimation**: Tracks tokens and calculates API costs
- **File Generation**: Automatically saves code to output directory
- **Modular Architecture**: Separate files for schemas, agents, and orchestration
- **Better Prompts**: Detailed system prompts with coding standards
- **Progress Tracking**: Visual progress with Rich library
- **Attempt Counter**: Tracks and limits retry attempts
- **Error Collection**: Aggregates all errors for debugging

## 📋 Requirements

- Python 3.11+
- Anthropic API key
- (Optional) E2B API key for real sandbox execution

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to directory
cd ai-dev-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Run the Agent

```python
from agent import run_agent

# Generate a feature
run_agent(
    user_request="Create a contact form with name, email, and message fields",
    output_dir="./generated/contact-form",
    max_attempts=3
)
```

Or run the example:

```bash
python agent.py
```

### 3. Enable E2B for Real Testing (Optional)

By default, the agent uses **simulated** test results. To run **real Playwright tests** in E2B cloud sandboxes:

```bash
# 1. Get E2B API key from https://e2b.dev
# 2. Add to .env file
echo "E2B_API_KEY=your_key_here" >> .env

# 3. Run with E2B enabled
python example_with_e2b.py
```

Or in code:
```python
run_agent(
    user_request="Your feature request",
    use_e2b=True  # Enable real testing!
)
```

**Note:** E2B costs ~$0.05 per test run. See [E2B_GUIDE.md](E2B_GUIDE.md) for full details.

## 📖 Usage Examples

### Example 1: Simple Form

```python
from agent import run_agent

run_agent(
    user_request="""
    Create a newsletter signup form with:
    - Email input field
    - Subscribe button
    - Success/error messages
    - Email validation
    """,
    output_dir="./generated/newsletter",
    max_attempts=3
)
```

### Example 2: CRUD Feature

```python
run_agent(
    user_request="""
    Build a todo list feature:
    - Add new todos with title and description
    - Mark todos as complete
    - Delete todos
    - Filter by status (all, active, completed)
    - Store in Firestore
    """,
    output_dir="./generated/todo-list",
    max_attempts=5
)
```

### Example 3: API Integration

```python
run_agent(
    user_request="""
    Create a weather widget:
    - Search for city
    - Display current temperature
    - Show 5-day forecast
    - Use FastAPI backend to fetch from weather API
    - Cache results in Firestore
    """,
    output_dir="./generated/weather-widget",
    max_attempts=4
)
```

## 🏗️ Architecture

```
┌─────────────┐
│   PLANNER   │  Creates technical blueprint
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  VERIFIER   │  Writes Playwright tests
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   BUILDER   │  Implements the code ◄─────┐
└──────┬──────┘                            │
       │                                   │
       ▼                                   │
┌─────────────┐                            │
│   SANDBOX   │  Runs tests ──[FAIL]───────┘
└──────┬──────┘
       │
   [PASS]
       │
       ▼
    SUCCESS!
```

### State Flow

1. **PLANNER** → Analyzes request → Creates `Blueprint`
2. **VERIFIER** → Reads blueprint → Creates `TestSuite`
3. **BUILDER** → Reads blueprint + tests → Creates `Implementation`
4. **SANDBOX** → Runs tests → Returns `SandboxResult`
5. **ROUTER** → If tests pass → END | If fail → Back to BUILDER

## 📊 Schemas

### Blueprint

```python
class Blueprint(BaseModel):
    feature_name: str
    description: str
    components: List[BlueprintComponent]
    api_endpoints: List[APIEndpoint]
    firestore_collections: List[FirestoreCollection]
    complexity: Literal["simple", "medium", "complex"]
    estimated_lines_of_code: int
    estimated_tokens: int
```

### TestSuite

```python
class TestSuite(BaseModel):
    file_name: str
    setup_code: Optional[str]
    test_cases: List[TestCase]
    mocked_api_responses: Dict[str, Dict]
```

### Implementation

```python
class Implementation(BaseModel):
    files: List[CodeFile]
    setup_instructions: List[str]
    testing_notes: str
```

## 🧪 Sandbox Integration

The current implementation uses **simulated** test results. To integrate real test execution:

### Option 1: E2B Integration

```python
from e2b import Sandbox

def sandbox_node(state: AgentState) -> dict:
    sandbox = Sandbox(template="node")

    # Copy test files
    for test_file in state['test_suite'].test_cases:
        sandbox.filesystem.write(f"tests/{test_file.name}.spec.ts", test_file.test_code)

    # Run tests
    result = sandbox.process.start("npx playwright test")

    return {
        "sandbox_result": SandboxResult(
            passed=result.exit_code == 0,
            logs=result.stdout
        )
    }
```

### Option 2: Docker Integration

```python
import subprocess

def sandbox_node(state: AgentState) -> dict:
    # Run tests in Docker container
    result = subprocess.run(
        ["docker", "run", "--rm", "-v", "./tests:/tests", "playwright-image", "npx", "playwright", "test"],
        capture_output=True,
        text=True
    )

    return {
        "sandbox_result": SandboxResult(
            passed=result.returncode == 0,
            logs=result.stdout
        )
    }
```

## 💰 Cost Tracking

The agent tracks costs in real-time based on Claude Sonnet 4 pricing (as of Jan 2025):

- **Input tokens**: $3.00 per 1M tokens
- **Output tokens**: $15.00 per 1M tokens

Example cost breakdown:

```
Planning:    500 input + 1000 output = $0.0165
Testing:     400 input +  800 output = $0.0132
Building:   1000 input + 3000 output = $0.0480
TOTAL:                                 $0.0777
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional - Model overrides
MODEL_PLANNER=claude-sonnet-4-20250514
MODEL_VERIFIER=claude-sonnet-4-20250514
MODEL_BUILDER=claude-sonnet-4-20250514

# Optional - Cost tracking
COST_PER_1M_INPUT_TOKENS=3.00
COST_PER_1M_OUTPUT_TOKENS=15.00
```

### Custom Tech Stack

Edit the prompts in `agent.py` to match your stack:

```python
PLANNER_SYSTEM_PROMPT = """
TECH STACK:
- Frontend: Your framework here
- Backend: Your backend here
- Database: Your database here
...
"""
```

## 🎯 Roadmap

- [ ] Real E2B sandbox integration
- [ ] Support for additional LLM providers (OpenAI, Gemini)
- [ ] Streaming output for real-time progress
- [ ] Git integration (auto-commit generated code)
- [ ] Web UI for non-CLI usage
- [ ] Multi-file editing (not just creation)
- [ ] Conversation history for iterative refinement
- [ ] Plugin system for custom agents
- [ ] Cost budgets and limits
- [ ] Performance benchmarking

## 🤝 Contributing

Contributions welcome! Areas of interest:

1. **Sandbox Integration** - Real test execution with E2B/Docker
2. **Additional Models** - Support GPT-4, Gemini Pro
3. **Better Prompts** - Improve system prompts for accuracy
4. **UI Improvements** - Better CLI visualization
5. **Testing** - Unit tests for agent nodes

## 📝 License

MIT

## 🙏 Credits

Inspired by:
- Lovable.dev
- Bolt.new
- v0.dev
- Original LangGraph agent by [user]

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Anthropic Claude](https://anthropic.com)
- [Rich](https://github.com/Textualize/rich)

---

**Made with ❤️ using Claude Sonnet 4**
