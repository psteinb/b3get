========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/b3get/badge/?style=flat
    :target: https://readthedocs.org/projects/b3get
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/psteinb/b3get.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/psteinb/b3get

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/psteinb/b3get?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/psteinb/b3get

.. |codecov| image:: https://codecov.io/github/psteinb/b3get/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/psteinb/b3get

.. |version| image:: https://img.shields.io/pypi/v/b3get.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/b3get

.. |commits-since| image:: https://img.shields.io/github/commits-since/psteinb/b3get/vv0.4.1..svg
    :alt: Commits since latest release
    :target: https://github.com/psteinb/b3get/compare/vv0.4.1....master

.. |wheel| image:: https://img.shields.io/pypi/wheel/b3get.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/b3get

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/b3get.svg
    :alt: Supported versions
    :target: https://pypi.org/project/b3get

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/b3get.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/b3get


.. end-badges

library to download image sets from Broad Bioimage Benchmark Collection images

* Free software: BSD 3-Clause License

Installation
============

::

    pip install b3get

Documentation
=============


https://b3get.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
