import random
import re
import pandas as pd


def process_column(
    df: pd.DataFrame, column: str, handler: str, prefix: str = None
) -> pd.DataFrame:
    """Process the given column using the specified handler.

    Args:
        df (pd.DataFrame): DataFrame to modify.
        column (str): Column name.
        handler (str): The handler to use.

    Returns:
        pd.DataFrame: The modified DataFrame.
        dict: A dictionary mapping each input column value to the output.
    """
    mappings = {}
    if handler == "FLOC":
        # Build FLOC map
        # Floc map maps hierarchy levels (1, 2, 3, etc) to unique
        # component values (ABC, etc)
        floc_map = {}
        for val in df[column]:
            components = re.split("-|\.", val)
            for i, c in enumerate(components):
                if (i + 1) not in floc_map:
                    floc_map[i + 1] = {}
                if c not in floc_map[i + 1]:
                    floc_map[i + 1][c] = str(len(floc_map[i + 1]) + 1)

        for i, row in df.iterrows():
            val = df.at[i, column]
            components = re.split("-|\.", val)

            col_out = "_".join(
                [floc_map[j + 1][c] for j, c in enumerate(components)]
            )

            mappings[str(df.at[i, column])] = col_out
            df.at[i, column] = col_out

    elif handler == "RandomiseInteger":
        # Generate random integer
        rs = random.sample(range(1000000, 9999999), len(df.index))
        x = 0
        for i, row in df.iterrows():
            mappings[str(df.at[i, column])] = rs[x]
            df.at[i, column] = rs[x]
            x += 1

    elif handler == "ToUniqueString":
        # Generate string identifier for each unique value
        prefix = prefix if prefix else ""
        string_map = {}
        for val in df[column]:
            if val not in string_map:
                string_map[val] = prefix + str(len(string_map) + 1)
        for i, row in df.iterrows():
            val = df.at[i, column]
            mappings[str(df.at[i, column])] = string_map[val]
            df.at[i, column] = string_map[val]

    elif handler == "None":
        for val in df[column]:
            mappings[str(val)] = str(val)

    return df, mappings
