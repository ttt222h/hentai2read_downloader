import typer
from rich.console import Console
from cli.commands import register_commands
from core.config import settings
from utils.logging_config import configure_logger

console = Console()

# Configure logger based on settings
configure_logger(settings)

app = typer.Typer(
    name="hentai2read-downloader",
    help="A modern, modular Python application for downloading manga from hentai2read.\n\nFor GUI mode, use: main.py --gui or main.py -g",
    no_args_is_help=True,
)

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """
    Manage and download manga from hentai2read.
    """
    if verbose:
        console.log("Verbose output enabled.")
    # You can attach common resources to the context here
    ctx.obj = {"verbose": verbose}

# Register commands from commands.py
register_commands(app)

if __name__ == "__main__":
    app()
