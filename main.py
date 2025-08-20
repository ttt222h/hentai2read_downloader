"""
Main Entry Point for H2Read Downloader

This module provides the main entry point that can launch
either the CLI or GUI interface based on command line arguments.
"""

import sys
import typer
from typing import Optional

from cli.app import app as cli_app
from core.config import Settings
from utils.logging_config import configure_logger


def main():
    """
    Main entry point for H2Read Downloader.
    """
    try:
        # Parse command line arguments manually
        gui = "--gui" in sys.argv or "-g" in sys.argv
        config_path = None
        
        # Check for config path argument
        for i, arg in enumerate(sys.argv):
            if arg in ["--config", "-c"] and i + 1 < len(sys.argv):
                config_path = sys.argv[i + 1]
                break
        
        # Load configuration
        config = Settings()
        if config_path:
            # TODO: Load config from file when implemented
            pass
        
        # Configure logger based on settings
        configure_logger(config)
        
        if gui:
            # Launch GUI interface
            from gui.app import run_gui
            exit_code = run_gui(config)
            sys.exit(exit_code)
        else:
            # Launch CLI interface (default)
            # Remove our arguments before passing to CLI app
            original_argv = sys.argv[:]
            filtered_argv = [arg for arg in sys.argv if arg not in ["--gui", "-g", "--config", "-c", config_path]]
            sys.argv = filtered_argv
            cli_app()
            sys.argv = original_argv
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
