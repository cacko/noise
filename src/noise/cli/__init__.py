import typer
from .app import meter

cli = typer.Typer()

@cli.command()
def console():
    """Run the noise monitor in console mode."""
    meter()


@cli.callback()
def main():
    pass