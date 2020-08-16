import typer
from sowba.core import path
from sowba.storage import StorageName
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException


def create_app(
    name, /, output="./", storage: StorageName = "rocksdb", template="default"
):
    try:
        cookiecutter(
            f"{path.template.app}/{template}",
            output_dir=output,
            no_input=True,
            extra_context={"app": name, "storage": storage.value},
        )
    except OutputDirExistsException:
        typer.echo(f"Eroor: App {name} alredy exist!")
        raise typer.Abort()


def add_service(app, service):
    try:
        pass
    except expression as identifier:
        pass
