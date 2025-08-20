from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.text import Text

console = Console()

def ask_text_input(prompt_message: str, default: str | None = None) -> str:
    """Asks the user for text input."""
    result = Prompt.ask(Text(prompt_message, style="bold cyan"), default=default)
    return result if result is not None else "" # Ensure a string is always returned

def ask_confirmation(prompt_message: str, default: bool = True) -> bool:
    """Asks the user for a yes/no confirmation."""
    return Confirm.ask(Text(prompt_message, style="bold cyan"), default=default)

def ask_delete_confirmation(prompt_message: str, default: bool = False) -> bool:
    """Asks the user for a yes/no confirmation regarding deletion, defaulting to No."""
    return Confirm.ask(Text(prompt_message, style="bold red"), default=default)

def select_from_list(prompt_message: str, choices: list) -> str:
    """Asks the user to select an item from a list of choices."""
    return Prompt.ask(Text(prompt_message, style="bold cyan"), choices=choices)

def ask_integer_input(prompt_message: str, default: int | None = None) -> int:
    """Asks the user for an integer input."""
    while True:
        try:
            # Prompt.ask returns a string, or an empty string if no input and no default
            value_str = Prompt.ask(
                Text(prompt_message, style="bold cyan"),
                default=str(default) if default is not None else "" # Ensure default is always a string for Prompt.ask
            )
            if value_str == "" and default is None:
                console.print(Text("Input cannot be empty. Please enter a valid integer.", style="bold red"))
                continue
            return int(value_str)
        except ValueError:
            console.print(Text("Invalid input. Please enter a valid integer.", style="bold red"))
