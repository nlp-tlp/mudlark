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


------------------
Command line usage
------------------

Once Mudlark is installed, you can run it via:

    python -m mudlark <function> <arguments>

There are currently two functions available:

- `normalise-csv` takes an input CSV file and 'normalises' it by running the text column of that CSV through a preprocessing pipeline.
- `normalise-text` does the same as the above, but on a single string.

To get a full list of the arguments, you can run:

    python -m mudlark normalise-csv --help

Or alternatively

    python -m mudlark normalise-text --help


.. list-table:: Required arguments
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
    * - input-path
      - Text
      - The path of the CSV to normalise. [required]
    * - output-path
      - Text
      - The path to save the normalised dataset to once complete. [required]
    * - text-column
      - Text
      - The name of the text column, for example'short text', 'risk name', etc. [required]
    * - output-format
      - Text
      - The format to save the output. Can be either 'csv' (saves the output as a CSV file) or 'quickgraph' (saves the output as a QuickGraph-compatible JSON file). [default: csv]

There are also several optional arguments:

.. list-table:: Optional arguments
    :widths: 35 25 50
    :header-rows: 1

    * - Argument
      - Type
      - Details
    * - corrections-path
      - Text
      -  The path containing the CSV to use for corrections. If not specified, the default corrections csv will be used.
    * - max-words
      - Integer
      -  If specified, documents with more than the specified number of words in the text column will be dropped.
    * - drop-duplicates
      - Boolean
      - If true, any rows with the same text in the text field as another row will be dropped. [default: False]
    * - csv-keep-columns
      - Text
      - If specified, only the given columns will be kept in the final output. Columns should be given as a comma separated list surrounded by double quotes, e.g. "col1, col2, col3"... This argument is only relevant when output_format = csv.
    * - quickgraph-id-columns
      - Text
      - If specified, the given column(s) will be used as id columns when generating output for QuickGraph. You may specify one column (for example 'my_id'), or multiple columns separated via comma (for example 'my_id, surname'). This argument is only relevant when output_format = quickgraph.