"""Tests for the normalise_csv function."""
import pytest
import filecmp
import pandas as pd
from mudlark import normalise_csv

# tests for quickgraph output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, options",
    [
        # Simple
        ("simple.csv", "simple_normalised_qg.json", "text", {}),
        # quickgraph_id_columns as 'text''
        (
            "simple.csv",
            "simple_normalised_qg_with_external_ids.json",
            "text",
            {"quickgraph_id_columns": "text"},
        ),
        (
            "simple_with_duplicates.csv",
            "simple_normalised_qg.json",
            "text",
            {"drop_duplicates": "yes"},
        ),
        # Testing max_words
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
        # If csv_keep_columns is set, it should still work (just log a warning)
        (
            "simple.csv",
            "simple_normalised_qg.json",
            "text",
            {"csv_keep_columns": "hello"},
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

    assert filecmp.cmp(output_path, expected_output_path)

# tests for csv output format
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, options",
    [
        ("simple.csv", "simple_normalised_csv.csv", "text", {}),
        (
            "simple.csv",
            "simple_normalised_csv_fewer_columns.csv",
            "text",
            {"csv_keep_columns": "text, cost"},
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
    output_path = tmp_path / "out.json"
    normalise_csv(
        input_path,
        text_field,
        output_format="csv",
        output_path=output_path,
        **options
    )

    assert filecmp.cmp(output_path, expected_output_path)

# tests for error handling with quickgraph output format 
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


# tests for error handling with csv output format 
@pytest.mark.parametrize(
    "input_path, text_field, options, error_type, error_snippet",
    [
        (
            "simple.csv",
            "text",
            {
                "output_format": "csv",
                "csv_keep_columns": "non_existent_column, cost",
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
        expected_output_path (str): The path of the expected output file.
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


@pytest.mark.parametrize(
    "input_path, text_field, options, num_rows",
    [
        ("simple.csv", "text", {}, 9),  #
        ("simple.csv", "text", {"max_rows": 5}, 5),  #
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
    """

    df = normalise_csv(input_path, text_field, **options)
    assert df.shape[0] == num_rows



# tests for custom corrections dictionary
@pytest.mark.parametrize(
    "input_path, expected_output_path, text_field, test_correction_dictionary_path, options",
    [
        # Testing new corrections dictionary 
        (
            "test_corrections.csv",
            "test_corrections_normalised_qg.json",
            "text",
            "dictionary_test_corrections.csv",
            {}
        ),
    ],
    indirect=["input_path", "expected_output_path", "test_correction_dictionary_path"],
)
def test_normalise_custom_corrections(
    input_path, expected_output_path, text_field, test_correction_dictionary_path, options, tmp_path
):
    """Ensure the normalise_text function works as expected with a custom corrections dictionary.
    At the moment, this always uses simple_normalise().

    Args:
        input_path (str): Path of input dataset.
        expected_output_path (str): Path of the expected output dataset.
        text_field (str): The text field in the CSV.
        test_correction_dictionary_path (str): Path of corrections dictionary.
        options (dict): The optional args for the normalise_csv function.
        tmp_path (object): pytest's tmp_path fixture (where the data will be
           temporarily saved).

    Deleted Parameters:
        input_dataset_path (str): The input path.
        output_dataset_path (str): The path of the expected output.
    """
    output_path = tmp_path / "out.json"
    normalise_csv(input_path, text_field, output_path=output_path, corrections_path=test_correction_dictionary_path, **options)

    assert filecmp.cmp(output_path, expected_output_path)