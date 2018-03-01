===================================================
Unitarizable Highest Weight Modules
===================================================
.. image:: https://travis-ci.org/vit-tucek/uhw_modules.svg?branch=master
    :target: https://travis-ci.org/vit-tucek/uhw_modules

This package is a `SageMath <http://www.sagemath.org>`_ package that contains all unitarizable highest weight modules organized into cones as in [DES]_ and calculates their nilpotent cohomology using Enright formula [E]_.

.. [DES] Davidson, Enright, Stanke: Differential operators and highest weight representations
.. [E] Enright: Analogues of Kostant's u-cohomology formulas for unitary highest modules

The full documentation for the package can be found at https://vit-tucek.github.io/uhw_modules/doc/html/


Installation
------------

Local install from source
^^^^^^^^^^^^^^^^^^^^^^^^^

Download the source from the git repository::

    $ git clone https://github.com/vit-tucek/uhw_modules.git

Change to the root directory and run::

    $ sage -pip install --upgrade --no-index -v .

For convenience this package contains a [makefile](makefile) with this
and other often used commands. Should you wish too, you can use the
shorthand::

    $ make install


Usage
-----

Once the package is installed, you can use it in Sage with::

    sage: from uhw_modules import answer_to_ultimate_question
    sage: answer_to_ultimate_question()
    42

Developer's guide
-----------------
Want to contribute or modify uhw_modules? Excellent! This section presents some useful information on what is included in the package.

Source code
^^^^^^^^^^^

All source code is stored in the folder ``uhw_modules``. All source folder
must contain a ``__init__.py`` file with needed includes.

Tests
^^^^^

This package is configured for tests written in the documentation
strings, also known as ``doctests``. For examples, see this
`source file <uhw_modules/ultimate_question.py>`_. See also
`SageMath's coding conventions and best practices document <http://doc.sagemath.org/html/en/developer/coding_basics.html#writing-testable-examples>`_.
With additional configuration, it would be possible to include unit
tests as well.

Once the package is installed, one can use the SageMath test system
configured in ``setup.py`` to run the tests::

    $ sage setup.py test

This is just calling ``sage -t`` with appropriate flags.

Shorthand::

    $ make test

Documentation
^^^^^^^^^^^^^

The documentation of the package can be generated using Sage's
``Sphinx`` installation::

    $ cd docs
    $ sage -sh -c "make html"

Shorthand::

    $ make doc
