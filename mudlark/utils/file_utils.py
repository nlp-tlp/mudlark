"""Functions for saving and loading files."""
import os
import pathlib
import json
from typing import Dict
import pandas as pd
from mudlark.logger import logger


def load_csv_file(path: str):
    """Use Pandas to load the CSV file at the given path.

    Args:
        path (str): The file to load.

    Returns:
        pd.DataFrame: The pandas dataframe.
    """
    df = pd.read_csv(
        path, engine="python", on_bad_lines="skip", skipinitialspace=True
    )
    return df


def load_corrections_dict(path: str = None) -> Dict:
    """Load the given corrections CSV and parse it into a dictionary.
    If path is empty or None, load the default instead.

    Args:
        path (str): The path of the corrections file.

    Returns:
        dict: The parsed dictionary of corrections.
    """

    if path == "" or path is None:
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve().parent.resolve(),
            "dictionaries",
            "mwo_corrections.csv",
        )

    df = load_csv_file(path)
    corrections_dict = df.set_index(df.columns[0])[df.columns[1]].to_dict()

    return corrections_dict


def save_to_quickgraph_json(
    df: pd.DataFrame,
    output_path: str,
    text_column: str,
    id_columns: list[str] = None,
):
    """Save the DataFrame to the given path.

    If using csv output, simply save the dataframe to the output path.

    If using quickgraph output, convert the dataframe to the quickgraph
    format, then save.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_path (str): The path to save it to.
        text_column (str): The text column.
        id_columns (list[str], optional): The list of id columns to use as the
           composite id (to save in the 'external_id' field)

    """
    output_data = []
    for _, row in df.iterrows():
        obj = {
            "tokens": row[text_column].split(),
            "original": row[text_column],
        }
        if id_columns:
            obj["external_id"] = _compile_external_id(row, id_columns)
        output_data.append(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"Saved output to {output_path}.")


def _compile_external_id(row: pd.Series, id_columns: list[str]):
    """Construct a 'compiled' id for the given row, given a list of
    id_columns. It will look something like this:

    Col1: Value1, Col2: Value2

    This is necessary to use for the "original_id" field in the QuickGraph
    output.

    Args:
        row (pd.Series): The row to compile the id for.
        id_columns (list[str]): The list of id columns.

    Returns:
        str: An id.
    """
    return ", ".join([f"{col}: {row[col]}" for col in id_columns])
