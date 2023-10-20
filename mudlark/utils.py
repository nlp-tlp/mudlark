import pandas as pd
import csv
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


def load_corrections_dict(path: str) -> Dict:
    """Load the given corrections CSV and parse it into a dictionary.

    Args:
        path (str): The path of the corrections file.

    Returns:
        dict: The parsed dictionary of corrections.
    """
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
