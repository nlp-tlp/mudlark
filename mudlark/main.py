"""The main functions of Mudlark, i.e. normalise_csv and normalise_text."""
import json
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
    load_corrections_dict,
    load_column_config,
)
from .column_processing import process_column
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
    anonymise_text_column: Annotated[
        bool,
        typer.Argument(
            help="Whether to anonymise asset identifiers in the text."
        ),
    ] = False,
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
    column_config_path: Annotated[
        Optional[str],
        typer.Option(help="If specified, ... TODO."),
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
    dump_anonymised_terms_path: Annotated[
        Optional[str],
        typer.Option(
            help="If specified, all terms that have been anonymised by "
            "mudlark will be dumped to the given path."
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
    column_config = None
    if column_config_path is not None:
        # If using quickgraph, this argument is not relevant - print a
        # warning message.
        if output_format == "quickgraph":
            logger.warning(
                "You appear to have set 'column_config_path', but this is "
                "being ignored as this argument is only relevant when "
                "output_format = csv."
            )

        column_config = load_column_config(column_config_path)

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
    if column_config and output_format == "csv":
        csv_keep_columns = [c.name for c in column_config.columns]
        df = drop_unwanted_columns(df, csv_keep_columns, text_column)

    # If drop_duplicates is True, drop rows accordingly
    if drop_duplicates == "True":
        df = run_drop_duplicates(df, text_column)

    # If max_words is present, drop all rows with > max_words
    if max_words:
        df = drop_long_rows(df, text_column, max_words)

    # If max rows, randomly sample
    if max_rows:
        df = df.sample(n=max_rows)
        logger.info(f"Randomly sampled to {len(df)} rows.")

    corrections_dict = load_corrections_dict(corrections_path)

    # Run the normalisation over each row, on the text column
    # Maintain a list of anonymised terms to dump later, if needed
    anonymised_terms = []
    num_rows = len(df.index)
    x = 0
    for i, row in df.iterrows():
        df.at[i, text_column], anons = simple_normalise(
            df.at[i, text_column],
            anonymise_text_column,
            corrections_dict,
            dump_anonymised_terms_path,
        )
        anonymised_terms += anons
        x += 1
        if x % 100 == 0 and x > 1:
            logger.info(f"Completed {x} of {num_rows} rows")
    anonymised_terms = sorted(list(set(anonymised_terms)))

    # TODO: Migrate to its own function
    # Map anonymised terms to IDs automatically
    # Make sure to map everything properly, e.g. ABC-123 and ABC 123
    # should both map to the same AssetID e.g. Asset5
    anonymised_terms_map = {}
    for term in anonymised_terms:
        term_normed = term.replace(" ", "").replace("-", "")
        if term_normed not in anonymised_terms_map:
            anonymised_terms_map[term_normed] = "Asset%d" % (
                len(anonymised_terms_map) + 1
            )

    if dump_anonymised_terms_path and len(anonymised_terms) > 0:
        with open(dump_anonymised_terms_path, "w", encoding="utf-8") as f:
            for i, term in enumerate(anonymised_terms):
                term_normed = term.replace(" ", "").replace("-", "")
                f.write(term + ", " + (anonymised_terms_map[term_normed]))
                f.write("\n")
        logger.info(
            f"Dumped {len(anonymised_terms)} anonymised terms to "
            f"{dump_anonymised_terms_path}"
        )

    # Process columns if specified
    if column_config and output_format == "csv":
        logger.info("Processing other columns...")
        mappings = {}
        for c in column_config.columns:
            logger.info(f"Processing '{c}'...")
            df, mappings[c.name] = process_column(
                df, c.name, c.handler, c.prefix
            )
        with open(column_config.output_path, "w", encoding="utf-8") as f:
            json.dump(mappings, f, indent=2)

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
