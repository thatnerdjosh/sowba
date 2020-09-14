import typer

app = typer.Typer()


@app.command()
def greetings(
    name: str = typer.Argument(...), formal: bool = typer.Option(False)
):
    if formal:
        typer.echo(f"Hello {name}!")
    else:
        typer.echo(f"Hey {name}!")


if __name__ == "__main__":
    app()
