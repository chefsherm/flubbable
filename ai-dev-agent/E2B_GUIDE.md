# E2B Integration Guide

This guide explains how to use E2B for **real test execution** instead of simulated tests.

## 🤔 What is E2B?

[E2B](https://e2b.dev) (Execution in 2 Billion) is a cloud sandbox platform that runs code in isolated environments. Think of it as "Docker in the cloud" - you get a real Ubuntu environment where you can install dependencies, run tests, and execute code safely.

### Why Use E2B?

| Simulated Tests | E2B Sandbox |
|----------------|-------------|
| ❌ Fake results | ✅ Real test execution |
| ❌ Can't catch real bugs | ✅ Catches actual errors |
| ❌ No confidence | ✅ Production-ready validation |
| ✅ Free | ⚠️ Paid (~$0.10/run) |
| ✅ Instant | ⚠️ Slower (30-60s) |

**Use E2B when:**
- You need to validate code before deployment
- You want to catch real bugs
- You're building production features
- Budget allows (~$0.10 per agent run)

**Use Simulation when:**
- Prototyping/learning
- Testing the agent workflow
- Running many iterations quickly
- Budget is tight

## 🚀 Quick Start

### 1. Get E2B API Key

```bash
# Visit https://e2b.dev and sign up
# Copy your API key from the dashboard
```

### 2. Install E2B

```bash
pip install e2b-code-interpreter
```

### 3. Configure Environment

```bash
# Add to .env file
E2B_API_KEY=your_api_key_here
```

Or export:
```bash
export E2B_API_KEY=your_api_key_here
```

### 4. Run with E2B Enabled

```python
from agent import run_agent

run_agent(
    user_request="Create a login form with validation",
    output_dir="./generated/login-form",
    use_e2b=True  # Enable E2B!
)
```

Or use the example:
```bash
python example_with_e2b.py
```

## 📖 How It Works

### Architecture

```
┌──────────────┐
│    AGENT     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   BUILDER    │ Generates code
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  E2B SANDBOX │
│              │
│  1. Create   │ Spin up cloud Ubuntu instance
│  2. Upload   │ Copy generated files
│  3. Install  │ npm install + Playwright browsers
│  4. Test     │ npx playwright test
│  5. Report   │ Return pass/fail + logs
│  6. Destroy  │ Clean up sandbox
│              │
└──────┬───────┘
       │
       ▼
   ✅ or ❌
```

### What Happens in E2B?

1. **Sandbox Creation** (~5s)
   - Creates a cloud Ubuntu environment
   - Node.js and npm pre-installed

2. **Project Setup** (~10s)
   - Copies generated code files
   - Creates `package.json`
   - Writes Playwright test files
   - Creates `playwright.config.ts`

3. **Dependencies** (~15s)
   - Runs `npm install`
   - Installs Playwright browsers
   - Downloads Chromium

4. **Test Execution** (~5-30s)
   - Starts Next.js dev server
   - Runs Playwright tests
   - Captures pass/fail results
   - Collects error messages

5. **Cleanup** (~1s)
   - Destroys sandbox
   - Returns results

**Total time: 30-60 seconds per test run**

## 💰 Cost Estimation

E2B pricing (as of January 2025):

| Metric | Cost |
|--------|------|
| Sandbox time | $0.001/second |
| Average run | 45 seconds |
| Cost per run | ~$0.045 |
| With retries (3x) | ~$0.135 |

**Monthly estimates:**
- 10 features: ~$1.35
- 50 features: ~$6.75
- 100 features: ~$13.50

Plus Claude API costs (~$0.08 per feature).

## 🔧 Advanced Configuration

### Custom Timeout

```python
from e2b_sandbox import E2BSandbox

with E2BSandbox(timeout=600) as sandbox:  # 10 minutes
    sandbox.run_tests()
```

### Debugging Failed Tests

E2B returns full Playwright logs:

```python
result = run_agent(..., use_e2b=True)

if not result['sandbox_result'].passed:
    print("Error messages:")
    for error in result['sandbox_result'].error_messages:
        print(f"  - {error}")

    print("\nFull logs:")
    print(result['sandbox_result'].logs)
```

### Manual Sandbox Control

```python
from e2b_sandbox import E2BSandbox
from schemas import Implementation, TestSuite

# Your implementation and tests
implementation = Implementation(...)
test_suite = TestSuite(...)

with E2BSandbox() as sandbox:
    # Setup
    sandbox.setup_nextjs_project(implementation, test_suite)
    sandbox.install_dependencies()

    # Run tests
    result = sandbox.run_tests()

    # Sandbox auto-cleaned up on exit
    print(f"Passed: {result.passed}")
```

## 🐛 Troubleshooting

### Error: "E2B_API_KEY not found"

```bash
# Make sure it's in .env
cat .env | grep E2B_API_KEY

# Or export it
export E2B_API_KEY=your_key_here
```

### Error: "Sandbox creation failed"

**Possible causes:**
1. Invalid API key
2. E2B service down
3. Network issues

**Solution:**
```python
# The agent automatically falls back to simulation
run_agent(..., use_e2b=True)  # Will use simulation if E2B fails
```

### Error: "npm install failed"

**Usually caused by:**
- Network timeout
- Invalid package.json

**Check logs:**
```python
result['sandbox_result'].logs
```

### Tests timeout

**Increase timeout:**
```python
from e2b_sandbox import E2BSandbox

# Increase from default 300s to 600s
with E2BSandbox(timeout=600) as sandbox:
    ...
```

### Playwright installation issues

E2B automatically installs Chromium. If it fails:

```python
# Check logs
print(result['sandbox_result'].logs)

# Look for:
# ✅ Browsers installed
# or
# ❌ Failed to install browsers
```

## 🎯 Best Practices

### 1. Use Simulation for Development

```python
# During development - fast iterations
run_agent(..., use_e2b=False)

# Before deployment - final validation
run_agent(..., use_e2b=True)
```

### 2. Handle Failures Gracefully

```python
result = run_agent(..., use_e2b=True)

final_state = list(result.values())[0]

if final_state['status'] == 'SUCCESS':
    # Deploy code
    deploy(final_state['implementation'])
else:
    # Review errors
    print("Failed tests:", final_state['sandbox_result'].error_messages)
```

### 3. Monitor Costs

```python
# Track E2B usage
runs = 0
total_time = 0

result = run_agent(..., use_e2b=True)
runs += final_state['attempt_count']
total_time += final_state['sandbox_result'].execution_time_ms

print(f"Total E2B runs: {runs}")
print(f"Total time: {total_time/1000}s")
print(f"Estimated cost: ${runs * 45 * 0.001:.2f}")
```

### 4. Cache Dependencies (Future)

E2B supports custom templates with pre-installed dependencies:

```bash
# Create custom template with deps pre-installed
e2b template create --name next-playwright

# Use template (reduces install time)
sandbox = Sandbox(template="next-playwright")
```

## 📊 Comparison: Simulation vs E2B

| Feature | Simulation | E2B |
|---------|-----------|-----|
| **Speed** | ⚡ Instant (<1s) | 🐢 Slow (30-60s) |
| **Cost** | 💰 Free | 💸 ~$0.045/run |
| **Accuracy** | ❌ Fake (always passes attempt #2) | ✅ Real bugs caught |
| **Reliability** | ⚠️ Not production-ready | ✅ Production validation |
| **Setup** | ✅ None | ⚠️ API key required |
| **Offline** | ✅ Works offline | ❌ Requires internet |
| **Use Case** | Prototyping, learning | Production, deployment |

## 🔮 Future Enhancements

Planned improvements to E2B integration:

- [ ] **Custom templates** - Pre-installed dependencies
- [ ] **Parallel testing** - Run multiple sandboxes at once
- [ ] **Screenshot capture** - Visual diffs on failure
- [ ] **Video recording** - Playwright trace files
- [ ] **Performance metrics** - Load time, bundle size
- [ ] **Accessibility tests** - Axe, Lighthouse scores
- [ ] **Mobile testing** - iOS Safari, Android Chrome
- [ ] **Backend testing** - FastAPI pytest integration

## 🆘 Support

**E2B Issues:**
- Docs: https://e2b.dev/docs
- Discord: https://e2b.dev/discord
- GitHub: https://github.com/e2b-dev/e2b

**Agent Issues:**
- Check `IMPROVEMENTS.md` for architecture details
- Review logs in `result['sandbox_result'].logs`
- Open GitHub issue with reproduction steps

## 📝 Example Output

### Successful E2B Run

```
🚀 AI Development Agent
Powered by Claude Sonnet 4
Testing: E2B Sandbox

--- 🧠 PLANNER: Creating Technical Blueprint ---
  ✅ Blueprint created: Contact Form Feature
  📊 Complexity: simple
  💰 Cost: $0.0165

--- 🕵️ VERIFIER: Writing Test Suite ---
  ✅ Test suite created: contact-form.spec.ts
  🧪 Test cases: 3
  💰 Cost: $0.0132

--- 👷 BUILDER: Writing Code (Attempt 1/3) ---
  ✅ Implementation complete: 4 files
  💰 Cost: $0.0480

--- 🧪 SANDBOX: Running Tests ---
  🚀 Using E2B for real test execution
  🔧 Creating E2B sandbox...
  ✅ Sandbox created
  📦 Setting up Next.js project...
    📄 Created: components/ContactForm.tsx
    📄 Created: app/page.tsx
    📄 Created: lib/validation.ts
    ✅ Created 3 test cases
  ✅ Project setup complete
  📥 Installing dependencies...
  ✅ Dependencies installed
  🌐 Installing Playwright browsers...
  ✅ Browsers installed
  🧪 Running Playwright tests...
  ✅ All tests passed! (3/3)
  🧹 Cleaning up sandbox...
  ✅ Sandbox closed

┌─ Test Results ─┐
│ Metric  │ Value │
├─────────┼───────┤
│ Total   │ 3     │
│ Passed  │ 3     │
│ Failed  │ 0     │
│ Time    │ 2347ms│
└─────────┴───────┘

✅ Feature Implementation Complete!

Final Summary
┌────────────┬──────────┐
│ Metric     │ Value    │
├────────────┼──────────┤
│ Attempts   │ 1        │
│ Tokens     │ 4,823    │
│ Cost       │ $0.0777  │
│ Status     │ SUCCESS  │
└────────────┴──────────┘

📁 Generated files saved to: ./generated/contact-form
```

---

**Ready to test with E2B? Run `python example_with_e2b.py`!** 🚀
