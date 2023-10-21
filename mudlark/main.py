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
        str, typer.Argument(help="The path of the CSV to normalise.")
    ],
    output_path: Annotated[
        str,
        typer.Argument(
            help="The path to save the normalised dataset to once complete."
        ),
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
        typer.Option(
            help="The path containing the CSV to use for corrections. "
            "If not specified, the default corrections csv will be used."
        ),
    ] = None,
    output_format: Annotated[
        str,
        typer.Argument(
            help="The format to save the output. Can be either 'csv' (saves "
            "the output as a CSV file) or 'quickgraph' (saves the output as "
            "a QuickGraph-compatible JSON file)."
        ),
    ] = "csv",
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
    id_columns: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, the given column(s) will be used as "
            "id columns when generating output for QuickGraph. You may "
            "specify one column (for example 'my_id'), or multiple columns "
            "separated via comma (for example 'my_id, surname')."
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

    # If the user has specified any 'keep columns',
    # load them into a list of strings.
    if keep_columns is not None:
        keep_columns = parse_list(keep_columns)

    # If the user has specified any 'id columns',
    # load them into a list of strings.
    if id_columns is not None:
        id_columns = parse_list(id_columns)

    # Load the corrections dictionary.
    # If it is not specified, the default one will be loaded.
    corrections_dict = load_corrections_dict(corrections_path)

    # Load the CSV into a DataFrame
    input_df = load_csv_file(input_path)

    # Normalise the DataFrame
    output_df = normalise_dataframe(
        input_df,
        output_path,
        text_column,
        corrections_dict,
        output_format,
        max_words,
        drop_duplicates,
        keep_columns,
        id_columns,
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
