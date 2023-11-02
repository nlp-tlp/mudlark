"""The main functions of Mudlark, i.e. normalise_csv and normalise_text."""
import typer
from typing_extensions import Annotated, Optional
from typer_config import use_yaml_config

from .logger import logger
from .utils import (
    load_csv_file,
    load_corrections_dict,
    parse_list,
    save_to_csv,
    save_to_quickgraph_json,
    validate_quickgraph_id_columns,
)
from .normalisation import normalise, normalise_dataframe

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
    output_format: Annotated[
        str,
        typer.Option(
            help="The format to save the output. Can be either 'csv' (saves "
            "the output as a CSV file) or 'quickgraph' (saves the output as "
            "a QuickGraph-compatible JSON file)."
        ),
    ] = "quickgraph",
    max_rows: Annotated[
        Optional[int],
        typer.Option(
            help="If specified, the output will be randomly sampled to "
            "contain the specified maximum number of rows."
        ),
    ] = None,
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
            help="If specified, documents with more than the specified number "
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
    csv_keep_columns: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, only the given columns will be "
            "kept in the final output. Columns should be given as a "
            "comma separated list surrounded by double quotes, e.g. "
            '"col1, col2, col3"...\n'
            "This argument is only relevant when output_format = csv."
        ),
    ] = None,
    quickgraph_id_columns: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, the given column(s) will be used as "
            "id columns when generating output for QuickGraph. You may "
            "specify one column (for example 'my_id'), or multiple columns "
            "separated via comma (for example 'my_id, surname').\n"
            "This argument is only relevant when output_format = quickgraph."
        ),
    ] = None,
):
    """Normalise the CSV located at the given path.

    Args:
        path (str): The path of the CSV to normalise.
        text_column (str): The name of the text column, for example
           'short text', 'risk name', etc.

    Returns
        pandas.DataFrame: The modified CSV as a DataFrame.
    """

    # Input validation
    if output_format not in ["csv", "quickgraph"]:
        raise ValueError("Output format must be either 'csv' or 'quickgraph'.")

    # If the user has specified any 'keep columns',
    # load them into a list of strings.
    if csv_keep_columns is not None:
        csv_keep_columns = parse_list(csv_keep_columns)
        # If using quickgraph, this argument is not relevant - print a
        # warning message.
        if output_format == "quickgraph":
            logger.warning(
                "You appear to have set 'csv_keep_columns', but this is "
                "being ignored as this argument is only relevant when "
                "output_format = csv."
            )

    # Load the CSV into a DataFrame
    input_df = load_csv_file(input_path)

    # If the user has specified any 'id columns',
    # load them into a list of strings.
    if quickgraph_id_columns is not None:
        quickgraph_id_columns = parse_list(quickgraph_id_columns)

        # If using QuickGraph output format, make sure the id_columns is
        # present and check that all id columns exist in the dataset.
        if output_format == "quickgraph":
            validate_quickgraph_id_columns(input_df, quickgraph_id_columns)
        else:
            # If not using QuickGraph, this argument is not relevant - print a
            # warning message.
            if quickgraph_id_columns:
                logger.warning(
                    "You appear to have set 'quickgraph_id_columns', but this "
                    "is being ignored as this argument is only relevant when "
                    "output_format = quickgraph."
                )

    # Load the corrections dictionary.
    # If it is not specified, the default one will be loaded.
    corrections_dict = load_corrections_dict(corrections_path)

    logger.info(f"Normalising csv: '{input_path}'")

    # Normalise the DataFrame
    output_df = normalise_dataframe(
        input_df,
        text_column,
        corrections_dict,
        output_format,
        max_rows,
        max_words,
        drop_duplicates,
        csv_keep_columns,
    )

    # Save the output to disk
    if output_format == "csv":
        save_to_csv(output_df, output_path)
    elif output_format == "quickgraph":
        save_to_quickgraph_json(
            output_df, output_path, text_column, quickgraph_id_columns
        )

    return output_df


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
    # logger.debug(f"{text} -> {normalised_text}")
    return normalised_text


if __name__ == "__main__":
    app()
