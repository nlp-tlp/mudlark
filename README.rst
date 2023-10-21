*******
mudlark
*******

Mudlark is a Python package for automatically cleaning the technical language present across many CSV-based datasets.

============
Installation
============

We plan to put Mudlark on PyPI soon, after which you will be able to run:

    pip install mudlark

=====
Usage
=====

Mudlark can be used two ways: via the command line, and directly in Python.


--------------------------------
Running Mudlark via command line
--------------------------------

Once Mudlark is installed, you can run it via:

    python -m mudlark <function> <arguments>

There are currently two functions available:

- ``normalise-csv`` takes an input CSV file and 'normalises' it by running the text column of that CSV through a preprocessing pipeline.
- ``normalise-text`` does the same as the above, but on a single string.

To get a full list of the arguments, you can run::

    python -m mudlark normalise-csv --help

Or alternatively::

    python -m mudlark normalise-text --help

^^^^^^^^^^^^^
normalise_csv
^^^^^^^^^^^^^

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
    * - ``output-format``
      - Text
      - The format to save the output. Can be either 'csv' (saves the output as a CSV file) or 'quickgraph' (saves the output as a QuickGraph-compatible JSON file). [default: csv]

Optional arguments:

.. list-table::
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
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

Here is an example:

* We are interested in normalising the dataset called ``test.csv``.
* We want to save the output to ``test_output.csv``.
* The text column within this csv file is called ``short_text``.
* We want to save it as a ``csv`` file.
* We are happy to use the default corrections CSV.
* We want to drop rows where the ``short_text`` column has > 15 words.
* We want to drop duplicates.
* We are happy to keep all of the columns in the output.

The command to do this would be::

    python -m mudlark normalise-csv test.csv test_output.csv short_text csv --max-words 15 --drop-duplicates true


"""""""""""""""""""""""
Using a config.yml file
"""""""""""""""""""""""

Writing out long commands can be tedious, so we have also made it possible to read the commands in from a yaml file. Simply create a yaml file (name it something like ``mudlark.yml``), specifying your arguments on each line::

    input_path: test.csv
    output_path: test_output.csv
    text_column: short_text
    output_format: csv
    max_words: 15
    drop_duplicates: true

Then, you can read it in via the ``config`` argument::

    python -m mudlark normalise-csv --config mudlark.yml

^^^^^^^^^^^^^^
normalise_text
^^^^^^^^^^^^^^

The ``normalise_text`` function is a lot simpler - just two arguments:

.. list-table::
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
    * - ``text``
      - Text
      - The text to normalise. [required]
    * - ``corrections-path``
      - Text
      - The path containing the CSV to use for corrections. If not specified, the default corrections csv will be used.

Note that this function does not currently support the use of a config yaml file (as it is only two arguments).

-------------------------
Running Mudlark in Python
-------------------------

This is a work in progress, but it should be possible to run Mudlark via Python as follows:

.. code-block:: python
    :linenos:

    from mudlark import normalise_csv

    # Normalising a CSV dataset
    normalise_csv('test.csv', 'test_output.csv', 'short_text', 'csv', max_words=15, drop_duplicates=True)

    # Normalising some text
    normalise_text('pmp is BRokeN')

The arguments are exactly the same as when running the function(s) via command line.

