"""Tests for the normalise_csv function."""
import pytest
import filecmp
import pandas as pd
from mudlark import normalise_csv


def _files_same(output_path, expected_output_path):
    return (
        open(output_path, "r").read() == open(expected_output_path, "r").read()
    )


# [1] tests for quickgraph output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, options",
    [
        # Simple
        ("simple.csv", "simple_normalised_qg.json", "text", {}),
        # quickgraph_id_columns as 'text'
        (
            "simple.csv",
            "simple_normalised_qg_with_external_ids.json",
            "text",
            {"quickgraph_id_columns": "text"},
        ),
        # Testing dropping duplicate rows
        (
            "simple_with_duplicates.csv",
            "simple_normalised_qg.json",
            "text",
            {"drop_duplicates": "yes"},
        ),
        # Testing dropping rows with more than the specified number of words in the text column
        (
            "simple.csv",
            "simple_normalised_qg.json",
            "text",
            {"max_words": 100},
        ),
        (
            "simple_with_long_rows.csv",
            "simple_normalised_qg.json",
            "text",
            {"max_words": 100},
        ),
    ],
    indirect=["input_path", "expected_output_path"],
)
def test_normalise_csv_to_quickgraph(
    input_path, expected_output_path, text_field, options, tmp_path
):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): Path of input dataset.
        expected_output_path (str): Path of the expected output dataset.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).

    Deleted Parameters:
        input_dataset_path (str): The input path.
        output_dataset_path (str): The path of the expected output.
    """
    output_path = tmp_path / "out.json"
    normalise_csv(input_path, text_field, output_path=output_path, **options)

    assert _files_same(output_path, expected_output_path)

    # assert filecmp.cmp(output_path, expected_output_path)


# [2] tests for csv output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, options",
    [
        ("simple.csv", "simple_normalised_csv.csv", "text", {}),
        (
            "simple.csv",
            "simple_normalised_csv_fewer_columns.csv",
            "text",
            {
                "column_config_path": "tests/test_datasets/config/column-config-1.yml"
            },
        ),
        # Testing dropping duplicate rows
        (
            "simple_with_duplicates.csv",
            "simple_normalised_csv.csv",
            "text",
            {"drop_duplicates": "yes"},
        ),
        # Testing dropping rows with more than the specified number of words in the text column
        (
            "simple.csv",
            "simple_normalised_csv.csv",
            "text",
            {"max_words": 100},
        ),
        (
            "simple_with_long_rows.csv",
            "simple_normalised_csv.csv",
            "text",
            {"max_words": 100},
        ),
        # If quickgraph_id_columns is set, it should still work, just log
        # a warning.
        (
            "simple.csv",
            "simple_normalised_csv.csv",
            "text",
            {"quickgraph_id_columns": "text"},
        ),
    ],
    indirect=["input_path", "expected_output_path"],
)
def test_normalise_csv_to_csv(
    input_path, expected_output_path, text_field, options, tmp_path
):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

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
    output_path = tmp_path / "out.csv"
    normalise_csv(
        input_path,
        text_field,
        output_format="csv",
        output_path=output_path,
        **options
    )

    assert _files_same(output_path, expected_output_path)


# [3] tests for error handling with quickgraph output format
@pytest.mark.parametrize(
    "input_path, text_field, options, error_type, error_snippet",
    [
        (
            "simple.csv",
            "text",
            {"quickgraph_id_columns": "non_existent_column"},
            ValueError,
            "listed in the id_columns does not exist",
        ),
        (
            "simple.csv",
            "text",
            {"output_format": "not_a_real_format"},
            ValueError,
            "Output format must be either",
        ),
        (
            "simple.csv",
            "text",
            {"corrections_path": "not_an_existing_path"},
            FileNotFoundError,
            "No such file or directory",
        ),
        (
            "simple.csv",
            "text",
            {"max_rows": "not_an_integer"},
            TypeError,
            "not supported between instances of 'str' and 'int'",
        ),
        (
            "simple.csv",
            "text",
            {"max_rows": 100},
            ValueError,
            "Cannot take a larger sample than population when 'replace=False'",
        ),
    ],
    indirect=["input_path"],
)
def test_normalise_csv_to_quickgraph_errors(
    input_path, text_field, options, error_type, error_snippet
):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): Path of input dataset.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        error_type (Exception): The type of expected Exception.
        error_snippet (str): A snippet that is expected to appear in the error
           message.
    """
    with pytest.raises(error_type) as e:
        normalise_csv(input_path, text_field, **options)
    assert error_snippet in str(e)


# [4] tests for error handling with csv output format
@pytest.mark.parametrize(
    "input_path, text_field, options, error_type, error_snippet",
    [
        (
            "simple.csv",
            "text",
            {
                "output_format": "csv",
                "column_config_path": (
                    "tests/test_datasets/config/column-config-2.yml"
                ),
            },
            ValueError,
            "was not found in the input dataset. Please check all columns",
        ),
    ],
    indirect=["input_path"],
)
def test_normalise_csv_to_csv_errors(
    input_path, text_field, options, error_type, error_snippet
):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): The path of the input file.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        error_type (Exception): The type of expected Exception.
        error_snippet (str): A snippet that is expected to appear in the error
           message.
    """
    with pytest.raises(error_type) as e:
        normalise_csv(input_path, text_field, **options)
        print(e)
    assert error_snippet in str(e)


# [5] Test for setting number of randomly sampled rows in quickgraph format, and checks
# normalise_csv also outputs a dataframe as expected when no output_path is specified
@pytest.mark.parametrize(
    "input_path, text_field, options, num_rows",
    [
        ("simple.csv", "text", {}, 9),
        ("simple.csv", "text", {"max_rows": 5}, 5),
    ],
    indirect=["input_path"],
)
def test_normalise_csv_to_df(input_path, text_field, options, num_rows):
    """Ensure normalise_csv also outputs a dataframe as expected when no
    output_path is specified.

    Args:
        input_path (str): The path of the input file.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        num_rows (int): The number of expected rows in the output quickgraph.
    """

    df = normalise_csv(input_path, text_field, **options)
    assert df.shape[0] == num_rows


# [6] Test for setting number of randomly sampled rows in csv format
@pytest.mark.parametrize(
    "input_path, text_field, options, num_rows",
    [
        ("simple.csv", "text", {}, 9),
        ("simple.csv", "text", {"max_rows": 5}, 5),
    ],
    indirect=["input_path"],
)
def test_normalise_csv_to_csv_max_rows(
    input_path, text_field, options, num_rows, tmp_path
):
    """Ensure the normalise_text function works as expected.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): The path of the input file.
        text_field (str): The text field in the CSV.
        options (dict): The optional args for the normalise_csv function.
        num_rows (int): The number of expected rows in the output CSV.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).
    """
    output_path = tmp_path / "out.csv"
    normalise_csv(
        input_path,
        text_field,
        output_path=output_path,
        output_format="csv",
        **options
    )
    df = pd.read_csv(output_path)

    assert df.shape[0] == num_rows


# [7] tests for custom corrections dictionary
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, out_format,\
    test_correction_dictionary_path, options",
    [
        # Output format quickgraph
        (
            "test_corrections.csv",
            "test_corrections_normalised_qg.json",
            "text",
            "quickgraph",
            "dictionary_test_corrections.csv",
            {},
        ),
        # Output format csv
        (
            "test_corrections.csv",
            "test_corrections_normalised_csv.csv",
            "text",
            "csv",
            "dictionary_test_corrections.csv",
            {},
        ),
    ],
    indirect=[
        "input_path",
        "expected_output_path",
        "test_correction_dictionary_path",
    ],
)
def test_normalise_custom_corrections(
    input_path,
    expected_output_path,
    text_field,
    out_format,
    test_correction_dictionary_path,
    options,
    tmp_path,
):
    """Ensure the normalise_text function works as expected with a custom corrections dictionary.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): Path of input dataset.
        expected_output_path (str): Path of the expected output dataset.
        text_field (str): The text field in the CSV.
        out_format (str): the format of output file, either 'quickgraph' or 'csv'.
        test_correction_dictionary_path (str): Path of corrections dictionary.
        options (dict): The optional args for the normalise_csv function.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).

    Deleted Parameters:
        input_dataset_path (str): The input path.
        output_dataset_path (str): The path of the expected output.
    """
    output_path = tmp_path / "out.json"
    normalise_csv(
        input_path,
        text_field,
        output_path=output_path,
        output_format=out_format,
        corrections_path=test_correction_dictionary_path,
        **options
    )

    assert _files_same(output_path, expected_output_path)
