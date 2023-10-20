import os
import typer
import pathlib
from typing_extensions import Annotated, Optional

from .utils import *

app = typer.Typer()


@app.command()
def normalise_csv(
    path: Annotated[
        str, typer.Argument(help="The path of the CSV to normalise.")
    ],
    text_column: Annotated[
        str,
        typer.Argument(
            help="The name of the text column, for example"
            "'short text', 'risk name', etc."
        ),
    ],
    corrections_path: Annotated[
        Optional[str],
        typer.Argument(
            help="The path containing the CSV." " to use for corrections."
        ),
    ] = None,
):
    """Normalise the CSV located at the given path.

    Args:
        path (str): The path of the CSV to normalise.
        text_column (str): The name of the text column, for example
           'short text', 'risk name', etc.
    """
    print(f"Normalising csv: '{path}'")

    if corrections_path is None:
        corrections_path = os.path.join(
            pathlib.Path(__file__).parent.resolve(),
            "dictionaries",
            "mwo_corrections.csv",
        )

    print("Corrections path:", corrections_path)

    corrections = load_corrections(corrections_path)


@app.command()
def normalise_sent(sent: str):
    """Normalise a single sentence, such as ``replace brokn pump''.

    Args:
        sent (str): The sentence to normalise.
    """
    print(f"Normalising string {sent}")


if __name__ == "__main__":
    app()
