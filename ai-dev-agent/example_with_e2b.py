"""
Example: Using E2B for Real Test Execution

This example demonstrates how to use E2B sandbox for actual test execution
instead of simulated results.

Requirements:
1. E2B API key (get from https://e2b.dev)
2. Set E2B_API_KEY environment variable
3. pip install e2b-code-interpreter

Note: E2B sandbox creates real cloud environments and may incur costs.
Check E2B pricing at https://e2b.dev/pricing
"""

import os
from agent import run_agent
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    # Check for E2B API key
    if not os.getenv("E2B_API_KEY"):
        console.print(Panel.fit(
            "❌ E2B_API_KEY not found!\n\n"
            "1. Get your API key from https://e2b.dev\n"
            "2. Add to .env file: E2B_API_KEY=your_key_here\n"
            "3. Run: export E2B_API_KEY=your_key_here",
            style="bold red"
        ))
        return

    console.print(Panel.fit(
        "🚀 E2B Sandbox Example\n\n"
        "This will create a REAL sandbox environment\n"
        "and execute Playwright tests.\n\n"
        "Cost: ~$0.10 per run (check E2B pricing)",
        style="bold cyan"
    ))

    # Simple example: Contact form
    run_agent(
        user_request="""
Create a simple contact form with:
- Name input (required)
- Email input (required, must be valid email)
- Message textarea (required, min 10 chars)
- Submit button
- Form validation
- Success message on submit

The form should prevent submission if validation fails.
        """.strip(),
        output_dir="./generated/contact-form-e2b",
        max_attempts=3,
        use_e2b=True  # Enable E2B!
    )

    console.print("\n" + "="*60)
    console.print(
        "\n✅ E2B execution complete!\n"
        "Check ./generated/contact-form-e2b for generated code.",
        style="bold green"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n👋 Interrupted. Goodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="bold red")
        import traceback
        traceback.print_exc()
