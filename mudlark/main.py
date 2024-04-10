"""The main functions of Mudlark, i.e. normalise_csv and normalise_text."""
import typer
from typing_extensions import Annotated, Optional
from typer_config import use_yaml_config

from .logger import logger
from .utils import (
    parse_list,
    validate_quickgraph_id_columns,
    drop_unwanted_columns,
    drop_duplicates as run_drop_duplicates,
    drop_long_rows,
    load_csv_file,
    save_to_quickgraph_json,
)
from .normalisation import simple_normalise

app = typer.Typer()


@app.command()
@use_yaml_config()
def normalise_csv(
    input_path: Annotated[
        str, typer.Argument(help="The path of the CSV to normalise.")
    ],
    text_column: Annotated[
        str,
        typer.Argument(
            help="The name of the text column, for example"
            "'short text', 'risk name', etc."
        ),
    ],
    output_path: Annotated[
        str,
        typer.Option(
            help="The path to save the normalised dataset to once complete."
        ),
    ] = None,
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
    df = load_csv_file(input_path)

    # Ensure the text column is always a string
    df[text_column] = df[text_column].astype(str)

    quickgraph_id_columns_list = None
    # If the user has specified any 'quickgraph id columns',
    # load them into a list of strings.
    if output_format == "quickgraph":
        # If using QuickGraph output format, make sure the id_columns is
        # present and check that all id columns exist in the dataset.
        quickgraph_id_columns_list = parse_list(quickgraph_id_columns)
        validate_quickgraph_id_columns(df, quickgraph_id_columns_list)
    elif quickgraph_id_columns:
        # If not using QuickGraph, this argument is not relevant - print a
        # warning message.
        logger.warning(
            "You appear to have set 'quickgraph_id_columns', but this "
            "is being ignored as this argument is only relevant when "
            "output_format = 'quickgraph'."
        )

    logger.info(f"Normalising csv: '{input_path}'")

    # If keep_columns is present, drop all columns not in this list
    # (and always keep the text_column).
    if csv_keep_columns and output_format == "csv":
        df = drop_unwanted_columns(df, csv_keep_columns, text_column)

    # If drop_duplicates is True, drop rows accordingly
    if drop_duplicates:
        df = run_drop_duplicates(df, text_column)

    # If max_words is present, drop all rows with > max_words
    if max_words:
        df = drop_long_rows(df, text_column, max_words)

    # Run the normalisation over each row, on the text column
    df[text_column] = df[text_column].apply(
        lambda x: simple_normalise(x, corrections_path)
    )

    # If max rows, randomly sample
    if max_rows:
        df = df.sample(n=max_rows)
        logger.info(f"Randomly sampled to {len(df)} rows.")

    if not output_path:
        return df
    # Save the output to disk
    if output_format == "csv":
        df.to_csv(output_path, index=False)
        logger.info(f"Saved output to {output_path}.")
    elif output_format == "quickgraph":
        save_to_quickgraph_json(
            df, output_path, text_column, quickgraph_id_columns_list
        )
    return df


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
    text = simple_normalise(text, corrections_path)

    return text


if __name__ == "__main__":
    app()  # pragma: no cover
