"""Command-line interface for Log Detective."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from src.parsers import detect_language, LanguageType
from src.parsers.detector import auto_parse, get_parser_for_language

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="log-detective")
def main() -> None:
    """Log Detective - AI-powered error log analysis tool."""
    pass


@main.command()
@click.option(
    "--file", "-f",
    type=click.Path(exists=True, path_type=Path),
    help="Path to log file to parse"
)
@click.option(
    "--text", "-t",
    type=str,
    help="Log text to parse directly"
)
@click.option(
    "--language", "-l",
    type=click.Choice(["java", "python", "auto"]),
    default="auto",
    help="Force specific language parser"
)
@click.option(
    "--output", "-o",
    type=click.Choice(["json", "table", "pretty"]),
    default="pretty",
    help="Output format"
)
def parse(
    file: Optional[Path],
    text: Optional[str],
    language: str,
    output: str
) -> None:
    """Parse error logs and extract stack traces."""
    # Get log text from file or direct input
    if file:
        log_text = file.read_text(encoding="utf-8", errors="replace")
    elif text:
        log_text = text
    else:
        # Read from stdin if no input provided
        if not sys.stdin.isatty():
            log_text = sys.stdin.read()
        else:
            console.print("[red]Error:[/red] Please provide --file or --text, or pipe input")
            sys.exit(1)

    if not log_text.strip():
        console.print("[yellow]Warning:[/yellow] Empty input")
        sys.exit(0)

    # Parse the log
    if language == "auto":
        detected_lang, errors = auto_parse(log_text)
    else:
        lang_type = LanguageType(language)
        detected_lang = lang_type
        parser = get_parser_for_language(lang_type)
        if parser:
            errors = parser.parse(log_text)
        else:
            console.print(f"[red]Error:[/red] No parser for language: {language}")
            sys.exit(1)

    # Output results
    if not errors:
        console.print(f"[yellow]No errors found[/yellow] (detected language: {detected_lang.value})")
        sys.exit(0)

    if output == "json":
        _output_json(errors, detected_lang)
    elif output == "table":
        _output_table(errors, detected_lang)
    else:
        _output_pretty(errors, detected_lang)


def _output_json(errors: list, language: LanguageType) -> None:
    """Output errors as JSON."""
    data = {
        "language": language.value,
        "error_count": len(errors),
        "errors": [e.to_dict() for e in errors]
    }
    console.print(json.dumps(data, indent=2, ensure_ascii=False))


def _output_table(errors: list, language: LanguageType) -> None:
    """Output errors as a table."""
    table = Table(title=f"Parsed Errors ({language.value})")

    table.add_column("#", style="dim", width=3)
    table.add_column("Type", style="red")
    table.add_column("Message", style="yellow", max_width=50)
    table.add_column("File", style="cyan")
    table.add_column("Line", style="green", justify="right")

    for i, error in enumerate(errors, 1):
        table.add_row(
            str(i),
            error.error_type,
            error.message[:50] + "..." if len(error.message) > 50 else error.message,
            error.file_path or "-",
            str(error.line_number) if error.line_number else "-"
        )

    console.print(table)


def _output_pretty(errors: list, language: LanguageType) -> None:
    """Output errors in pretty format."""
    console.print(f"\n[bold]Found {len(errors)} error(s)[/bold] (language: {language.value})\n")

    for i, error in enumerate(errors, 1):
        # Header
        severity_color = {
            "critical": "red bold",
            "error": "red",
            "warning": "yellow",
            "info": "blue"
        }.get(error.severity.value, "white")

        console.print(Panel(
            f"[{severity_color}]{error.error_type}[/{severity_color}]: {error.message}",
            title=f"Error #{i}",
            subtitle=f"Severity: {error.severity.value.upper()}"
        ))

        # Stack frames
        if error.stack_frames:
            console.print("  [bold]Stack Trace:[/bold]")
            for j, frame in enumerate(error.stack_frames[:5]):  # Limit to 5 frames
                prefix = "  → " if j == 0 else "    "
                location = frame.file_path
                if frame.line_number:
                    location += f":{frame.line_number}"
                method = f"{frame.class_name}.{frame.method_name}" if frame.class_name else frame.method_name
                console.print(f"{prefix}[cyan]{location}[/cyan] in [yellow]{method}[/yellow]")

                if frame.code_context:
                    console.print(f"       [dim]{frame.code_context}[/dim]")

            if len(error.stack_frames) > 5:
                console.print(f"    [dim]... and {len(error.stack_frames) - 5} more frames[/dim]")

        console.print()


@main.group()
def config() -> None:
    """Manage configuration."""
    pass


@config.command("init")
def config_init() -> None:
    """Initialize configuration file."""
    console.print("[yellow]Configuration init not yet implemented[/yellow]")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    console.print(f"[yellow]Setting {key}={value} not yet implemented[/yellow]")


@main.command()
@click.option("--repo", "-r", type=str, help="Repository path or URL")
def index(repo: Optional[str]) -> None:
    """Index source code for analysis."""
    console.print("[yellow]Indexing not yet implemented (Week 2-3)[/yellow]")


@main.group()
def github() -> None:
    """GitHub repository operations."""
    pass


@github.command("sync")
@click.option("--repo", "-r", type=str, required=True, help="GitHub repository URL")
def github_sync(repo: str) -> None:
    """Sync and index a GitHub repository."""
    console.print(f"[yellow]GitHub sync for {repo} not yet implemented (Week 4)[/yellow]")


@github.command("status")
def github_status() -> None:
    """Show GitHub sync status."""
    console.print("[yellow]GitHub status not yet implemented (Week 4)[/yellow]")


@main.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Log file to analyze")
@click.option("--text", "-t", type=str, help="Error text to analyze")
def analyze(file: Optional[str], text: Optional[str]) -> None:
    """Analyze error logs using AI."""
    console.print("[yellow]AI analysis not yet implemented (Week 6-7)[/yellow]")


@main.command()
@click.option("--file", "-f", type=click.Path(exists=True), required=True, help="Log file to watch")
def watch(file: str) -> None:
    """Watch log file for errors in real-time."""
    console.print(f"[yellow]Watching {file} not yet implemented (Week 9)[/yellow]")


@main.group()
def history() -> None:
    """Manage error history database."""
    pass


@history.command("search")
@click.option("--error", "-e", type=str, required=True, help="Error to search for")
def history_search(error: str) -> None:
    """Search for similar errors in history."""
    console.print(f"[yellow]History search for '{error}' not yet implemented (Week 6)[/yellow]")


@history.command("add")
@click.option("--error", "-e", type=str, required=True, help="Error description")
@click.option("--solution", "-s", type=str, required=True, help="Solution description")
def history_add(error: str, solution: str) -> None:
    """Add an error-solution pair to history."""
    console.print("[yellow]History add not yet implemented (Week 6)[/yellow]")


if __name__ == "__main__":
    main()
