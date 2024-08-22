Installation
============

Mudlark is available on PyPI (`link <https://pypi.org/project/mudlark/>`_). You can install Mudlark via ``pip``::

    pip install mudlark

You can also install Mudlark by cloning this repository and running::

    pip install poetry
    poetry install

The first time after installing, you'll need to install the NLTK files via::

    poetry shell
    python
    >> import nltk
    >> nltk.download("punkt_tab")