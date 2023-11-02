"""A logger that is a bit nicer than the default Python logger."""
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<level>{level}</level>\t{message}",
    filter="mudlark",
    level="DEBUG",
)
