import os
import sys
import typer
import pathlib
from typing import List
from typing_extensions import Annotated, Optional
from loguru import logger

from .utils import *

app = typer.Typer()
logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<level>{level}</level>\t{message}",
    filter="mudlark",
    level="DEBUG",
)


@app.command()
def normalise_csv(
    path: Annotated[
        str, typer.Argument(help="The path of the CSV to normalise.")
    ],
    text_column: Annotated[
        str,
        typer.Argument(
            help="The name of the text column, for example"
            "'short text', 'risk name', etc."
        ),
    ],
    config_path: Annotated[
        Optional[str],
        typer.Option(
            help="The path containing the config file. If not present, "
            "Mudlark will attempt to load 'mudlark.ini' if it exists. "
            "Failing that, the default config will be used. See the README "
            "for details on how to structure the config file."
        ),
    ] = None,
):
    """Normalise the CSV located at the given path.

    Args:
        path (str): The path of the CSV to normalise.
        text_column (str): The name of the text column, for example
           'short text', 'risk name', etc.
    """
    logger.info(f"Normalising csv: '{path}'")

    # Load the config.
    if config_path is None:
        if os.path.isfile("mudlark.ini"):
            config_path = "mudlark.ini"
        else:
            config_path = os.path.join(
                pathlib.Path(__file__).parent.resolve().parent.resolve(),
                "default.ini",
            )
    config = load_config(config_path)
    logger.debug(config)

    # If the user has specified any 'keep columns' in the config,
    # load them into a list of strings.
    if config["keep_columns"] is not None:
        keep_columns = extract_keep_columns(config["keep_columns"])

    # Load the corrections dictionary.
    # If it is blank in the config, load the default one.
    corrections_path = config["corrections_path"]
    if config["corrections_path"] == "":
        corrections_path = os.path.join(
            pathlib.Path(__file__).parent.resolve(),
            "dictionaries",
            "mwo_corrections.csv",
        )
    corrections = load_csv_file(corrections_path)


@app.command()
def normalise_sent(sent: str):
    """Normalise a single sentence, such as ``replace brokn pump''.

    Args:
        sent (str): The sentence to normalise.
    """
    print(f"Normalising string {sent}")


if __name__ == "__main__":
    app()
