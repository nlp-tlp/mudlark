Usage
=====

Mudlark can be used two ways: via the command line, and directly in Python.

Running Mudlark via command line
--------------------------------

You can run Mudlark via::

    python -m mudlark <arguments>

To get a full list of the arguments, you can run::

    python -m mudlark --help

A full list of required arguments and optional arguments are shown in the tables below.

.. list-table::
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
    * - ``input-path``
      - Text
      - The path of the CSV to normalise. [required]
    * - ``text-column``
      - Text
      - The name of the text column, for example'short text', 'risk name', etc. [required]

Optional arguments:

.. list-table::
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
    * - ``output-format``
      - Text
      - The format to save the output. Can be either 'quickgraph' (saves the output as a QuickGraph-compatible JSON file) or 'csv' (saves the output as a CSV file). [default: quickgraph]
    * - ``output-path``
      - Text
      - The path to save the normalised dataset to once complete.
    * - ``max-rows``
      - Integer
      - If specified, the output will be randomly sampled to contain the specified maximum number of rows.
    * - ``corrections-path``
      - Text
      - The path containing the CSV to use for corrections. If not specified, the default corrections csv will be used. If using your own CSV file, it should have two columns. The first column contains the incorrect term, the second column contains the replacement for that term. Your first row should be a header row and contain 'wrong' in the first column and 'correct' in the second. See `here <https://github.com/nlp-tlp/mudlark/blob/main/mudlark/dictionaries/mwo_corrections.csv>`_ for the expected file format.
    * - ``max-words``
      - Integer
      -  If specified, documents with more than the specified number of words in the text column will be dropped.
    * - ``drop-duplicates``
      - Boolean
      - If true, any rows with the same text in the text field as another row will be dropped. [default: False]
    * - ``csv-keep-columns``
      - Text
      - If specified, only the given columns will be kept in the final output. Columns should be given as a comma separated list surrounded by double quotes, e.g. "col1, col2, col3"... This argument is only relevant when output_format = csv.
    * - ``quickgraph-id-columns``
      - Text
      - If specified, the given column(s) will be used as id columns when generating output for QuickGraph. You may specify one column (for example 'my_id'), or multiple columns separated via comma (for example 'my_id, surname'). This argument is only relevant when output_format = quickgraph.

Simple example
^^^^^^^^^^^^^^

Consider the following example:

* We are interested in normalising the dataset called ``test.csv``.
* We want to save the output to ``test_output.csv``.
* The text column within this csv file is called ``short_text``.
* We want to save it as a QuickGraph-compatible JSON file (the default output format).
* We want to limit the output to 100 rows (randomly sampled).
* We are happy to use the default corrections CSV.
* We want to drop rows where the ``short_text`` column has > 15 words.
* We want to drop duplicates.
* We will use the "ID" and "short_text" columns to form an identifier in our output QuickGraph data.

The command to do this would be::

    python -m mudlark test.csv "short_text" --output-path test_output.csv --max-rows 100 --max-words 15 --drop-duplicates true --quickgraph-id-columns "ID, short_text"

Using a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^

Writing out long commands can be tedious, so we have also made it possible to read the commands in from a yaml file. Simply create a yaml file (name it something like ``mudlark.yml``), specifying your arguments on each line::

    input_path: test.csv
    output_path: test_output.csv
    text_column: short_text
    max_rows: 100
    max_words: 15
    drop_duplicates: true
    quickgraph_id_columns: "ID, short_text"

Then, you can read it in via the ``config`` argument::

    python -m mudlark --config mudlark.yml

Note that the arguments have underscores (``_``) instead of dashes (``-``) when written in the yaml file.

Running Mudlark in Python
-------------------------

Mudlark can also be run directly in Python:

.. code-block:: python

    from mudlark import normalise_csv

    # Normalising a CSV dataset
    normalise_csv('test.csv', 'test_output.csv', 'short_text', max_rows=100, max_words=15, drop_duplicates=True, quickgraph_id_columns: "ID, short_text")

The arguments are exactly the same as when running the function via command line.

Mudlark also provides a simple function for normalising a single piece of text. The first argument is the text to normalise, and the second optional argument allows you to specify your own corrections dictionary:

.. code-block:: python

    from mudlark import normalise_text

    # Normalising some text
    normalise_text('pmp is  BRokeN')

    # Using your own corrections dictionary
    normalise_text('pmp is BRokeN', 'my_corrections.csv')


Running the tests
-----------------

If you would like to run the test cases, you can use::

    poetry run pytest --cov mudlark --cov-report html

The coverage report will be saved into the `htmlcov` folder.