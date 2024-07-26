Anonymisation
=============

Mudlark can now be used to fully anonymise a Maintenance Work Order CSV file. In this section we will cover anonymising the text column, and anonymising other columns.

Anonymising text
----------------

To anonymise text, simply set the ``anonymise_text`` argument to True, either via command line or in a config file.

When this is set to true, any terms that Mudlark deems to be "asset identifiers" will be anonymised and replaced with a unique asset identifier. For example, given the following data::

    text
    ABC 124 is broken
    ABC 123 has a problem
    ABC-124 is broken
    pumps busted
    enGiNe was broken
    a leak was Formed

The result will be::

    text
    Asset1 is broken
    Asset2 has a problem
    Asset1 is broken
    pump bust
    engine is broken
    a leak is form

Note how both ``ABC 124`` and ``ABC-124`` both become ``Asset1`` and ``ABC 123`` becomes ``Asset2``.

Some further notes on how this works:

* Currently a term is recognised as an asset identifier if it has one or more uppercase letter(s), followed by either nothing, a space, or a hyphen, then followed by one or more digit.
* The order is randomised prior to generating the numbers for each asset identifier.

Anonymising/processing other columns
------------------------------------

Mudlark can also anonymise and/or process other columns. To do this, set ``column_config_path`` prior to running Mudlark (either via command line or in a config file). An example column config file might look like this::

    columns:
      - name: floc
        handler: FLOC
      - name: mwo_id
        handler: RandomiseInteger
      - name: unique_floc_desc
        handler: ToUniqueString
        prefix: FLOC_Desc_
      - name: other
        handler: None

This file dictates which columns should be kept by Mudlark, and how it should handle each of them. There are currently four available "handlers":

* ``None`` simply passes the column through to the output file without doing anything to it.
* ``RandomiseInteger`` replaces each unique value of the column with a randomised integer (with 7 digits).
* ``FLOC`` treats the column as a Functional Location. It splits it based on either a ``.`` or a ``-``, then converts each unique value of each level of the FLOC hierarchy into a number. For example, ``123-45-67`` might become ``1-1-1``, ``123-45-68`` might become ``1-1-2``, and so on.
* ``ToUniqueString`` converts each unique value into an anonymised string, starting with the given ``prefix``. For example, ``Pump FLOC`` might become ``FLOC_Desc_1``, ``Belt FLOC`` might become ``FLOC_Desc_2``, and so on.

Example
-------

Here is an example dataset::

    text,cost,other,floc,mwo_id,unique_floc_desc
    ABC 124 is broken,123,test,123.45.67,123,FLOC 123
    replace,43,xx,123.45.68,123,FLOC 124
    X/X,540,test,123.45.69,123,FLOC 125
    ABC 123 has a problem,3,test,123.45.67,123,FLOC 123
    slurries,4.3,xx,123.45.67,123,FLOC 123
    ABC-124 is broken,4.33,yrds,123.45.67,123,FLOC 123
    pumps busted,43.43,tyrdtrd,111.45.67,123,FLOC 125
    enGiNe was broken,4332.3,6t554,112.45.67,123,FLOC 126
    a leak was Formed,333,545,113.45.67,123,FLOC 127

We are going to anonymise the text (as discussed in the first section), and will keep the ``floc``, ``mwo_id``, and ``unique_floc_desc`` columns. Here is our ``column-config.yml``::

    columns:
      - name: floc
        handler: FLOC
      - name: mwo_id
        handler: RandomiseInteger
      - name: unique_floc_desc
        handler: ToUniqueString
        prefix: FLOC_Desc_
      - name: other
        handler: None

And our Mudlark config file::

    input_path: my-file.csv
    output_path: my-file-out.csv
    text_column: text
    output_format: csv
    anonymise_text: true
    column_config: column-config.yml

Once we run Mudlark, the output will be::

    text,other,floc,mwo_id,unique_floc_desc
    Asset1 is broken,test,1_1_1,2462749,FLOC_Desc_1
    replace,xx,1_1_2,7832383,FLOC_Desc_2
    x/x,test,1_1_3,5472030,FLOC_Desc_3
    Asset2 has a problem,test,1_1_1,2806910,FLOC_Desc_1
    slurry,xx,1_1_1,1640112,FLOC_Desc_1
    Asset1 is broken,yrds,1_1_1,7360650,FLOC_Desc_1
    pump bust,tyrdtrd,2_1_1,9995977,FLOC_Desc_3
    engine is broken,6t554,3_1_1,6573352,FLOC_Desc_4
    a leak is form,545,4_1_1,6717645,FLOC_Desc_5
