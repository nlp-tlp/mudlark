# Mudlark

[![Pytest Status](https://github.com/nlp-tlp/mudlark/actions/workflows/run-tests.yml/badge.svg)](https://github.com/nlp-tlp/mudlark/actions/workflows/run-tests.yml) [![Coverage Status](https://coveralls.io/repos/github/nlp-tlp/mudlark/badge.svg?branch=main)](https://coveralls.io/github/nlp-tlp/mudlark?branch=main) [![Pylint Status](https://github.com/nlp-tlp/badges/blob/main/mudlark-pylint-badge.svg)](https://github.com/nlp-tlp/mudlark/actions/workflows/run-pylint.yml)

This library is designed to provide utilities for cleaning CSV datasets that contain technical language. Mudlark has three main purposes:

-  Rapid and easy preprocessing of CSV datasets that have a text column
-  Exporting a CSV dataset to a JSON file that can be readily imported into [QuickGraph](https://quickgraph.tech>), so that you can annotate the textual portion of your CSV dataset
-  Normalising a single piece of text which involves replacing any words appearing in a predefined "corrections dictionary" with suitable replacements. You can view this dictionary [here](https://github.com/nlp-tlp/mudlark/blob/main/mudlark/dictionaries/mwo_corrections.csv>`).

Note that at this stage, the pipeline-based normalisation method that we use is designed for maintenance work orders, but it is also applicable to other domains featuring similar technical language.

<p align="center">📘📗📙 <strong>Full README and code documentation available on <a href="https://mudlark.readthedocs.io/en/latest/">ReadtheDocs</a>.</strong> 📙📗📘</p>
