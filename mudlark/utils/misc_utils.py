"""Misc utility functions."""
import pandas as pd
from mudlark.logger import logger


def parse_list(s: str):
    """Parse the given comma-separated string into a list.

    Args:
        s (str): The string to parse.

    Returns:
        list: The list.
    """
    if s is None:
        return []
    return [i.strip() for i in s.split(",")]


def validate_quickgraph_id_columns(df: pd.DataFrame, id_columns: list[str]):
    """Validate that the id_columns are present, and that they all exist
    in the dataset.
    This is only checked when using the QuickGraph output format, as it
    requires an "external_id" that is comprised of the concatenation of these
    id_columns.

    Args:
        df (pd.DataFrame): The DataFrame.
        id_columns (list[str]): The list of id columns.

    Raises:
        ValueError: If any cols are not in the dataset.
    """
    if len(id_columns) == 0:
        logger.warning(
            "The quickgraph_id_columns is not set, so the output "
            "will not include an original_id column that maps back to your "
            "original dataset. Consider setting quickgraph_id_columns as "
            "discussed in the README."
        )
        return
    for col in id_columns:
        if col not in df:
            raise ValueError(
                f"The column '{col}' that is listed in the "
                "id_columns does not exist in the dataset."
            )
