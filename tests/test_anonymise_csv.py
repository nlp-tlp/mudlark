"""Tests for the normalise_csv function."""
import pytest
import filecmp
import pandas as pd
import random
from mudlark import normalise_csv


def _files_same(output_path, expected_output_path):
    return (
        open(output_path, "r", encoding="utf-8").read()
        == open(expected_output_path, "r", encoding="utf-8").read()
    )


# [2] tests for csv output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, options",
    [
        (
            "anonymisable_columns.csv",
            "anonymisable_columns_out.csv",
            "text",
            {
                "column_config_path": (
                    "tests/test_datasets/config/column-config-anon-1.yml"
                )
            },
        )
    ],
    indirect=["input_path", "expected_output_path"],
)
def test_anonymise_csv_columns(
    input_path, expected_output_path, text_field, options, tmp_path
):
    """Ensure the anonymise function works as expected.

    Args:
        input_path (str): The path of the input file.
        expected_output_path (str): The path of the expected output file.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).

    Deleted Parameters:
        input_dataset_path (str): The input path.
        output_dataset_path (str): The path of the expected output.
    """
    random.seed(123)
    output_path = tmp_path / "out.csv"
    output_anonymised_columns_path = tmp_path / "anonymised_columns.json"
    normalise_csv(
        input_path,
        text_field,
        output_format="csv",
        output_path=output_path,
        **options
    )

    assert _files_same(output_path, expected_output_path)


# [2] tests for csv output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, expected_output_terms_path, text_field, options",
    [
        (
            "anonymisable_columns_and_text.csv",
            "anonymisable_columns_and_text_out.csv",
            "anonymisable_terms_out.csv",
            "text",
            {
                "column_config_path": (
                    "tests/test_datasets/config/column-config-anon-1.yml"
                ),
                "anonymise_text": True,
            },
        ),
    ],
    indirect=[
        "input_path",
        "expected_output_path",
        "expected_output_terms_path",
    ],
)
def test_anonymise_csv_all(
    input_path,
    expected_output_path,
    expected_output_terms_path,
    text_field,
    options,
    tmp_path,
):
    """Ensure the anonymise function works as expected.

    Args:
        input_path (str): The path of the input file.
        expected_output_path (str): The path of the expected output file.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).

    Deleted Parameters:
        input_dataset_path (str): The input path.
        output_dataset_path (str): The path of the expected output.
    """
    random.seed(123)
    output_path = tmp_path / "out.csv"
    # output_anonymised_terms_path = tmp_path / "anonymised_terms.csv"
    output_anonymised_terms_path = tmp_path / "anonymised_terms.json"

    # output_anonymised_terms_path = "outterms.csv"

    normalise_csv(
        input_path,
        text_field,
        output_format="csv",
        output_path=output_path,
        **options,
        dump_anonymised_terms_path=output_anonymised_terms_path
    )

    with open(output_anonymised_terms_path, "r", encoding="utf-8") as f:
        d = f.read()
        print(d)

    assert _files_same(output_path, expected_output_path)
    assert _files_same(
        output_anonymised_terms_path, expected_output_terms_path
    )
