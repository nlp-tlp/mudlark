import os
import csv
import pathlib
import pandas as pd
from typing import List, Dict
import re


def load_csv_file(path: str):
    """Use Pandas to load the CSV file at the given path.

    Args:
        path (str): The file to load.

    Returns:
        pd.DataFrame: The pandas dataframe.
    """
    df = pd.read_csv(path, engine="python", on_bad_lines="skip")
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
            pathlib.Path(__file__).parent.resolve(),
            "dictionaries",
            "mwo_corrections.csv",
        )

    corrections_csv = load_csv_file(path)
    corrections_dict = corrections_csv.set_index("wrong")["correct"].to_dict()
    return corrections_dict


def parse_keep_columns(kc: str) -> List[str]:
    """Extract the 'keep columns' from the user-specified string.
    It should be a list of columns the user wants to keep,
    separated by comma.

    Args:
        kc (str): The string to parse.

    Returns:
        list[str]: The list of columns.
    """
    return [s.strip() for s in kc.split(",")]
