"""Utility functions for working with DataFrames."""
import pandas as pd
from mudlark.logger import logger


def drop_unwanted_columns(
    df: pd.DataFrame, keep_columns: list, text_column: str
) -> pd.DataFrame:
    """Remove any columns in the given DataFrame that are not listed in
    keep_columns.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        keep_columns (list): The list of columns that should be kept.
        text_column (str): The text column. This will always be kept.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    for c in keep_columns:
        if c not in df:
            raise ValueError(
                f"The column '{c}' was not found in the input dataset. "
                "Please check all columns listed in the 'keep_columns' list "
                "exist in the input dataset."
            )

    cols_before = len(df.columns)
    df = df[df.columns.intersection(keep_columns + [text_column])]
    cols_after = len(df.columns)
    logger.info(f"Dropped {cols_before - cols_after} unwanted columns.")

    return df


def drop_duplicates(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """Remove duplicate rows.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        text_column (str): The text column (duplicates of this column
           will be dropped).

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    rows_before = len(df)
    df = df.drop_duplicates(subset=text_column, keep="first")
    rows_after = len(df)
    logger.info(
        f"Dropped {rows_before - rows_after} duplicate rows "
        f"({rows_before} -> {rows_after})."
    )
    return df


def drop_long_rows(
    df: pd.DataFrame, text_column: str, max_words: int
) -> pd.DataFrame:
    """Remove rows where the text column has > max_words.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        text_column (str): The text column (duplicates of this column
           will be dropped).
        max_words (int): The max words allowed in the text column.

    No Longer Returned:
        pd.DataFrame: The modified DataFrame.
    """
    rows_before = len(df)
    df = df[df[text_column].apply(lambda x: len(x.split()) < max_words)]
    rows_after = len(df)
    logger.info(
        f"Dropped {rows_before - rows_after} rows with > {max_words} "
        f"words ({rows_before} -> {rows_after})."
    )
    return df
