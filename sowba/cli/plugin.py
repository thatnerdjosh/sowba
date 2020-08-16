"""
sowba plugin ls
sowba plugin add [name]
"""
import typer
from enum import Enum


app = typer.Typer()


class PluginName(str, Enum):
    user: str = "user"
    cache: str = "cache"


@app.command()
def ls(plugin: PluginName = typer.Argument(None)):
    if plugin is None:
        typer.echo("Plugin list")
    else:
        typer.echo(f"Plugin info: {plugin}")


@app.command()
def add(name: PluginName):
    typer.echo(f"Adding plugin: {name}")


if __name__ == "__main__":
    app()
