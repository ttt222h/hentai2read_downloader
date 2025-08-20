from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TransferSpeedColumn

console = Console()

def display_welcome_message():
    """Displays a welcome message for the CLI."""
    message = Text("Welcome to Hentai2Read Downloader CLI!", style="bold green")
    panel = Panel(message, border_style="blue", expand=False)
    console.print(panel)

def display_error(message: str):
    """Displays an error message."""
    console.print(Panel(Text(f"Error: {message}", style="bold red"), border_style="red"))

def display_info(message: str):
    """Displays an informational message."""
    console.print(Panel(Text(message, style="bold cyan"), border_style="cyan"))

def create_progress_bar(description: str):
    """Creates a Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        TransferSpeedColumn(),
        console=console,
    )

def create_manga_table(manga_list: list):
    """Creates a Rich table to display manga search results."""
    table = Table(title="Manga Search Results", style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="green")
    table.add_column("Chapters", style="yellow", justify="right")

    for i, manga in enumerate(manga_list):
        # Assuming manga object has a 'chapters' attribute which is a list
        chapter_count = len(manga.chapters) if hasattr(manga, 'chapters') else "N/A"
        table.add_row(str(i + 1), manga.title, str(chapter_count))
    return table

def display_progress_status(progress):
    """Displays the current download progress status."""
    status_message = f"[bold]{progress.current_chapter}[/bold]: [cyan]{progress.downloaded_images}/{progress.total_images}[/cyan] images downloaded. Status: [bold]{progress.status.upper()}[/bold]"
    if progress.errors:
        status_message += f" [red]Errors: {len(progress.errors)}[/red]"
    console.print(status_message)
