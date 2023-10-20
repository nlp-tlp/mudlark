import os
import sys
import typer
from typing import List
from typing_extensions import Annotated, Optional
from typer_config import use_yaml_config

from .logger import logger
from .utils import *
from .normalisation import normalise_text as normalise, normalise_dataframe
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
            help="If true, any rows with the same text in the text field "
            "as another row will be dropped."
        ),
    ] = False,
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
    corrections_dict = load_corrections_dict(corrections_path)

    # Load the CSV into a DataFrame
    input_df = load_csv_file(input_path)

    # Normalise the DataFrame
    output_df = normalise_dataframe(
        input_df, text_column, corrections_dict, max_words, drop_duplicates
    )


@app.command()
def normalise_text(
    text: Annotated[
        str,
        typer.Argument(help="The text to normalise."),
    ],
    corrections_path: Annotated[
        Optional[str],
        typer.Option(
            help="The path containing the CSV to use for corrections. "
            "If not specified, the default corrections csv will be used."
        ),
    ] = None,
):
    """Normalise a single sentence, such as ``replace brokn pump''.

    Args:
        text (str): The text to normalise.
        corrections_path (str): The path containing the CSV to use for
           corrections. If not specified, the default corrections csv
           will be used.
    """
    corrections_dict = load_corrections_dict(corrections_path)
    normalised_text = normalise(text, corrections_dict)
    logger.debug(f"{text} -> {normalised_text}")
    return normalise_text


if __name__ == "__main__":
    app()
