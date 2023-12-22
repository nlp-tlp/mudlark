.. Mudlark documentation master file, created by
   sphinx-quickstart on Fri Dec 22 13:54:46 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mudlark
===================================

Mudlark is a Python package for automatically cleaning the technical language present across many CSV-based datasets.

It is designed for the rapid and easy preprocessing of CSV datasets that have a text column, for example:

.. list-table::
    :widths: 20 20 20
    :header-rows: 1

    * - ID
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


.. toctree::
   :maxdepth: 2
   :caption: Contents:


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
