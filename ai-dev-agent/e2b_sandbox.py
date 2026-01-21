"""
E2B Sandbox Integration for Real Test Execution

This module provides integration with E2B for executing Playwright tests
in a real sandbox environment instead of simulation.
"""

import os
import time
from typing import Optional, List, Dict
from pathlib import Path

from e2b_code_interpreter import Sandbox
from rich.console import Console

from schemas import TestSuite, Implementation, SandboxResult

console = Console()


class E2BSandbox:
    """E2B Sandbox manager for test execution"""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 300):
        """
        Initialize E2B sandbox

        Args:
            api_key: E2B API key (defaults to E2B_API_KEY env var)
            timeout: Maximum execution time in seconds
        """
        self.api_key = api_key or os.getenv("E2B_API_KEY")
        self.timeout = timeout
        self.sandbox: Optional[Sandbox] = None

    def __enter__(self):
        """Context manager entry - create sandbox"""
        console.print("  🔧 Creating E2B sandbox...", style="cyan")
        self.sandbox = Sandbox(api_key=self.api_key, timeout=self.timeout)
        console.print("  ✅ Sandbox created", style="green")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup sandbox"""
        if self.sandbox:
            console.print("  🧹 Cleaning up sandbox...", style="cyan")
            self.sandbox.close()
            console.print("  ✅ Sandbox closed", style="green")

    def setup_nextjs_project(self, implementation: Implementation, test_suite: TestSuite):
        """
        Set up a Next.js project in the sandbox

        Args:
            implementation: Generated code files
            test_suite: Test suite to run
        """
        console.print("  📦 Setting up Next.js project...", style="cyan")

        # Create package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "test": "playwright test",
                "test:headed": "playwright test --headed"
            },
            "dependencies": {
                "next": "^14.1.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@playwright/test": "^1.40.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.2.0",
                "typescript": "^5.3.0"
            }
        }

        # Write package.json
        self.sandbox.filesystem.write(
            "/home/user/package.json",
            str(package_json).replace("'", '"')
        )

        # Write implementation files
        for code_file in implementation.files:
            file_path = f"/home/user/{code_file.file_path}"
            self.sandbox.filesystem.make_dir(str(Path(file_path).parent))
            self.sandbox.filesystem.write(file_path, code_file.content)
            console.print(f"    📄 Created: {code_file.file_path}", style="dim")

        # Write test files
        test_dir = "/home/user/tests"
        self.sandbox.filesystem.make_dir(test_dir)

        # Write test setup
        if test_suite.setup_code:
            self.sandbox.filesystem.write(
                f"{test_dir}/setup.ts",
                test_suite.setup_code
            )

        # Write individual test cases
        for i, test_case in enumerate(test_suite.test_cases):
            test_file = f"{test_dir}/{test_suite.file_name}"
            # Combine all test cases into one file
            if i == 0:
                test_content = f"""
import {{ test, expect }} from '@playwright/test';

{test_case.test_code}
"""
            else:
                # Append to existing content
                existing = self.sandbox.filesystem.read(test_file)
                test_content = existing + "\n\n" + test_case.test_code

            self.sandbox.filesystem.write(test_file, test_content)

        console.print(f"    ✅ Created {len(test_suite.test_cases)} test cases", style="green")

        # Create Playwright config
        playwright_config = """
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: false,
    timeout: 120 * 1000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
"""
        self.sandbox.filesystem.write(
            "/home/user/playwright.config.ts",
            playwright_config
        )

        console.print("  ✅ Project setup complete", style="green")

    def install_dependencies(self):
        """Install npm dependencies"""
        console.print("  📥 Installing dependencies...", style="cyan")

        result = self.sandbox.commands.run("cd /home/user && npm install")

        if result.exit_code != 0:
            console.print(f"  ⚠️ npm install warnings:\n{result.stderr}", style="yellow")
        else:
            console.print("  ✅ Dependencies installed", style="green")

        # Install Playwright browsers
        console.print("  🌐 Installing Playwright browsers...", style="cyan")
        result = self.sandbox.commands.run("cd /home/user && npx playwright install chromium")

        if result.exit_code == 0:
            console.print("  ✅ Browsers installed", style="green")

    def run_tests(self) -> SandboxResult:
        """
        Run Playwright tests in the sandbox

        Returns:
            SandboxResult with test execution details
        """
        console.print("  🧪 Running Playwright tests...", style="cyan")

        start_time = time.time()

        # Run Playwright tests
        result = self.sandbox.commands.run(
            "cd /home/user && npm test",
            timeout=self.timeout
        )

        execution_time_ms = (time.time() - start_time) * 1000

        # Parse test results
        output = result.stdout + result.stderr
        logs = output

        # Simple parsing (Playwright output format)
        passed_tests = output.count("✓")
        failed_tests = output.count("✗")
        total_tests = passed_tests + failed_tests

        # Extract error messages
        error_messages = []
        if "Error:" in output or "AssertionError:" in output:
            # Extract error lines
            for line in output.split("\n"):
                if "Error:" in line or "expected" in line.lower():
                    error_messages.append(line.strip())

        passed = result.exit_code == 0 and failed_tests == 0

        if passed:
            console.print(f"  ✅ All tests passed! ({passed_tests}/{total_tests})", style="bold green")
        else:
            console.print(f"  ❌ Tests failed: {failed_tests}/{total_tests}", style="bold red")

        return SandboxResult(
            passed=passed,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            error_messages=error_messages[:10],  # Limit to 10 errors
            execution_time_ms=execution_time_ms,
            logs=logs[-5000:]  # Last 5000 chars to avoid huge logs
        )


def run_tests_in_e2b_sandbox(
    implementation: Implementation,
    test_suite: TestSuite,
    api_key: Optional[str] = None
) -> SandboxResult:
    """
    Convenience function to run tests in E2B sandbox

    Args:
        implementation: Generated code implementation
        test_suite: Test suite to execute
        api_key: Optional E2B API key

    Returns:
        SandboxResult with test execution details
    """
    try:
        with E2BSandbox(api_key=api_key) as sandbox:
            # Setup project
            sandbox.setup_nextjs_project(implementation, test_suite)

            # Install dependencies
            sandbox.install_dependencies()

            # Run tests
            result = sandbox.run_tests()

            return result

    except Exception as e:
        console.print(f"  ❌ E2B sandbox error: {str(e)}", style="bold red")
        return SandboxResult(
            passed=False,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            error_messages=[f"E2B Error: {str(e)}"],
            execution_time_ms=0,
            logs=f"Failed to execute tests in E2B sandbox: {str(e)}"
        )
