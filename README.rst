*******
mudlark
*******

Mudlark is a Python package for automatically cleaning the technical language present across many CSV-based datasets.

It is designed for the rapid and easy preprocessing of CSV datasets that have a text column, for example:

.. list-table::
    :widths: 20 20 20
    :header-rows: 1

    * - id
      - short_text
      - date
    * - 0
      - pummp is Broken
      - 21/02/2022
    * - 1
      - seal leaking
      - 22/03/2022
    * - 2
      - repl broken seal
      - 25/03/2022

Using Mudlark, you can take this dataset and normalise (clean) the text column (in this case, ``short_text``), and save the cleaned CSV to disk. You can also export it to a JSON file that can be readily imported into `QuickGraph <https://quickgraph.tech>`_, so that you can annotate the textual portion of your CSV dataset.

Mudlark also has a few other smaller features, such as the ability to drop rows where the text column contains too many words, the ability to drop duplicate rows, and so on.

We also provide a simple function to normalise a single piece of text, detailed below.

Note that at this stage, the pipeline-based normalisation method that we use is designed for maintenance work orders, but it is also applicable to other domains featuring similar technical language.

Part of the normalisation stage involves replacing any words appearing in a predefined "corrections dictionary" with suitable replacements. You can view this dictionary `here <https://github.com/nlp-tlp/mudlark/blob/main/mudlark/dictionaries/mwo_corrections.csv>`_. We also provide options for using your own corrections dictionary, as detailed below.

============
Installation
============

Mudlark is available on PyPI (`link <https://pypi.org/project/mudlark/>`_). You can install Mudlark via ``pip``::

    pip install mudlark

You can also install Mudlark by cloning this repository and running::

    pip install poetry
    poetry install

=====
Usage
=====

Mudlark can be used two ways: via the command line, and directly in Python.

--------------------------------
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
    * - ``output-path``
      - Text
      - The path to save the normalised dataset to once complete. [required]
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
    * - ``max-rows``
      - Integer
      - If specified, the output will be randomly sampled to contain the specified maximum number of rows.
    * - ``corrections-path``
      - Text
      - The path containing the CSV to use for corrections. If not specified, the default corrections csv will be used.
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

^^^^^^^^^^^^^^
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
* We will use the "ID" and "short_text" columns to form an "ID" in our output QuickGraph data.

The command to do this would be::

    python -m mudlark test.csv test_output.csv "short_text" --max-rows 100 --max-words 15 --drop-duplicates true --quickgraph-id-columns "ID, short_text"

^^^^^^^^^^^^^^^^^^^^^^^^^^
Using a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^

Writing out long commands can be tedious, so we have also made it possible to read the commands in from a yaml file. Simply create a yaml file (name it something like ``mudlark.yml``), specifying your arguments on each line::

    input_path: test.csv
    output_path: test_output.csv
    text_column: short_text
    output_format: csv
    max_words: 15
    drop_duplicates: true

Then, you can read it in via the ``config`` argument::

    python -m mudlark --config mudlark.yml

Note that the arguments have underscores (``_``) instead of dashes (``-``) when written in the yaml file.

-------------------------
Running Mudlark in Python
-------------------------

Mudlark can also be run directly in Python:

.. code-block:: python

    from mudlark import normalise_csv

    # Normalising a CSV dataset
    normalise_csv('test.csv', 'test_output.csv', 'short_text', 'csv', max_words=15, drop_duplicates=True)

The arguments are exactly the same as when running the function via command line.

Mudlark also provides a simple function for normalising a single piece of text. The first argument is the text to normalise, and the second optional argument allows you to specify your own corrections dictionary:

.. code-block:: python

    from mudlark import normalise_text

    # Normalising some text
    normalise_text('pmp is BRokeN')

    # Using your own corrections dictionary
    normalise_text('pmp is BRokeN', 'my_corrections.csv')



