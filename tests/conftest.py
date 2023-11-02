"""Fixtures for the tests."""
import pytest
import os
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_datasets"


@pytest.fixture
def input_path(request):
    """Return the path of the given dataset e.g. test.csv.

    Args:
        request (object): The request object.

    Returns:
        str: The dataset path.
    """
    name = request.param
    return os.path.join(FIXTURE_DIR, "input", f"{name}")


@pytest.fixture
def expected_output_path(request):
    """Return the path of the given dataset e.g. test.csv.

    Args:
        request (object): The request object.

    Returns:
        str: The dataset path.
    """
    name = request.param
    return os.path.join(FIXTURE_DIR, "output", f"{name}")
