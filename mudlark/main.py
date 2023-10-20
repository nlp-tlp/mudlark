import os
import sys
import typer
import pathlib
from typing import List
from typing_extensions import Annotated, Optional
from typer_config import use_yaml_config

from .logger import logger
from .utils import *
from .normalisation import normalise_text, normalise_dataframe
from .config import *

app = typer.Typer()


@app.command()
@use_yaml_config()
def normalise_csv(
    input_path: Annotated[
        str, typer.Option(help="The path of the CSV to normalise.")
    ],
    text_column: Annotated[
        str,
        typer.Option(
            help="The name of the text column, for example"
            "'short text', 'risk name', etc."
        ),
    ],
    corrections_path: Annotated[
        Optional[str],
        typer.Option(
            help="The path containing the CSV to use for corrections. "
            "If not specified, the default corrections csv will be used."
        ),
    ] = None,
    max_words: Annotated[
        Optional[int],
        typer.Option(
            help="If true, documents with more than the specified number "
            "of words in the text column will be dropped."
        ),
    ] = None,
    drop_duplicates: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, any rows containing a duplicate value for "
            "the specified column will be dropped."
        ),
    ] = None,
    keep_columns: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, only the given columns will be "
            "kept in the final output. Columns should be given as a "
            "comma separated list surrounded by double quotes, e.g. "
            '"col1, col2, col3"...'
        ),
    ] = None,
):
    """Normalise the CSV located at the given path.

    Args:
        path (str): The path of the CSV to normalise.
        text_column (str): The name of the text column, for example
           'short text', 'risk name', etc.
    """

    logger.info(f"Normalising csv: '{input_path}'")

    # If the user has specified any 'keep columns' in the config,
    # load them into a list of strings.
    if keep_columns is not None:
        keep_columns = parse_keep_columns(keep_columns)

    # Load the corrections dictionary.
    # If it is not specified, load the default one.
    if corrections_path == "" or corrections_path is None:
        corrections_path = os.path.join(
            pathlib.Path(__file__).parent.resolve(),
            "dictionaries",
            "mwo_corrections.csv",
        )
    corrections_dict = load_corrections_dict(corrections_path)

    n = normalise_text("rePLACE pmp", corrections_dict)

    input_data = load_csv_file(input_path)

    normalise_dataframe(input_data, corrections_dict, drop_duplicates)


@app.command()
def normalise_sent(sent: str):
    """Normalise a single sentence, such as ``replace brokn pump''.

    Args:
        sent (str): The sentence to normalise.
    """
    print(f"Normalising string {sent}")


if __name__ == "__main__":
    app()
