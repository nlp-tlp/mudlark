import os
import pathlib
import configparser
from .logger import logger


# def load_config(user_config_path: str = None):
#     """Load the config.
#     Start by loading the base config (default.ini).
#     Overwrite the keys/values from the base config with the keys/values from
#     the user config.

#     Args:
#         user_config_path (str): The path of the user's config file.

#     Returns:
#         dict: The config, as a dictionary.
#     """

#     logger.debug("Loading base config...")
#     config = _load_config_file(
#         os.path.join(
#             pathlib.Path(__file__).parent.resolve().parent.resolve(),
#             "default.ini",
#         )
#     )

#     user_config = {}
#     if user_config_path is not None:
#         user_config = _load_config_file(user_config_path)

#     for k, v in user_config.items():
#         config[k] = v

#     return config


def load_config_file(path: str):
    """Load the config from the given file.

    Args:
        path (str): The ini file to load.

    Returns:
        dict: A dictionary representation of the config.

    Raises:
        OSError: If the path does not exist.
    """
    if not os.path.isfile(path):
        raise OSError(f"Config path {path} does not exist.")
    config = configparser.ConfigParser()
    config.read(path)
    logger.debug(f"Loaded config at {path} successfully.")
    return {k: v for (k, v) in config.items("DEFAULT")}
