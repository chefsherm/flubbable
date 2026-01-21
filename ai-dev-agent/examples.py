"""
Example use cases for the AI Development Agent
Run this file to try different feature implementations
"""

from agent import run_agent
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

console = Console()


# Predefined examples
EXAMPLES = {
    "1": {
        "name": "Feedback Form",
        "request": """
Create a feedback form component with:
- Title input field (required, max 100 chars)
- Description textarea (required, max 500 chars)
- Submit button
- Form validation
- Success message after submission
- Store submissions in Firestore 'feedback' collection
        """.strip(),
        "output_dir": "./generated/feedback-form"
    },
    "2": {
        "name": "User Profile Card",
        "request": """
Build a user profile card component that:
- Displays avatar image
- Shows user name, email, and bio
- Has edit button (only shows if logged in user)
- Fetch data from FastAPI endpoint /api/users/{id}
- Use Zustand for state management
        """.strip(),
        "output_dir": "./generated/user-profile"
    },
    "3": {
        "name": "Todo List (CRUD)",
        "request": """
Create a full todo list feature:
- Add new todos with title and description
- Mark todos as complete/incomplete (checkbox)
- Delete todos with confirmation
- Filter: All, Active, Completed
- Store in Firestore 'todos' collection
- FastAPI endpoints: GET, POST, PATCH, DELETE
        """.strip(),
        "output_dir": "./generated/todo-list"
    },
    "4": {
        "name": "Search Bar with Debounce",
        "request": """
Implement a search bar component:
- Input field with search icon
- Debounced search (300ms delay)
- Shows loading spinner while searching
- Displays results in dropdown
- Calls FastAPI /api/search endpoint
- Keyboard navigation (up/down arrows)
- Accessible (ARIA labels)
        """.strip(),
        "output_dir": "./generated/search-bar"
    },
    "5": {
        "name": "Image Upload Widget",
        "request": """
Build an image upload component:
- Drag and drop area
- File size validation (max 5MB)
- Image type validation (jpg, png, webp)
- Preview before upload
- Upload to Firebase Storage
- Save URL to Firestore
- Progress bar during upload
        """.strip(),
        "output_dir": "./generated/image-upload"
    }
}


def show_menu():
    """Display example menu"""
    console.print(Panel.fit(
        "🤖 AI Development Agent - Examples\n"
        "Choose a feature to generate",
        style="bold white on blue"
    ))

    console.print("\n[bold cyan]Available Examples:[/bold cyan]\n")

    for key, example in EXAMPLES.items():
        console.print(f"  [yellow]{key}[/yellow]. {example['name']}")

    console.print(f"  [yellow]0[/yellow]. Custom (write your own)")
    console.print(f"  [yellow]q[/yellow]. Quit\n")


def run_example():
    """Interactive example runner"""
    show_menu()

    choice = Prompt.ask(
        "[bold green]Select an example[/bold green]",
        choices=list(EXAMPLES.keys()) + ["0", "q"],
        default="1"
    )

    if choice == "q":
        console.print("👋 Goodbye!", style="bold blue")
        return

    if choice == "0":
        console.print("\n[bold cyan]Custom Feature Request[/bold cyan]")
        console.print("Describe the feature you want to build:")
        console.print("[dim](Press Ctrl+D or Ctrl+Z when done)[/dim]\n")

        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        request = "\n".join(lines).strip()
        output_dir = Prompt.ask(
            "\n[bold green]Output directory[/bold green]",
            default="./generated/custom-feature"
        )
    else:
        example = EXAMPLES[choice]
        console.print(f"\n[bold cyan]Selected: {example['name']}[/bold cyan]")
        console.print(f"\n[dim]Request:[/dim]\n{example['request']}\n")

        request = example['request']
        output_dir = example['output_dir']

    max_attempts = IntPrompt.ask(
        "[bold green]Max retry attempts[/bold green]",
        default=3
    )

    console.print(f"\n[bold yellow]Starting agent...[/bold yellow]\n")

    # Run the agent
    run_agent(
        user_request=request,
        output_dir=output_dir,
        max_attempts=max_attempts
    )


if __name__ == "__main__":
    try:
        run_example()
    except KeyboardInterrupt:
        console.print("\n\n👋 Interrupted. Goodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="bold red")
