Installation
============

LAPA-NG uses Poetry for dependency management. To install:

1. Install Poetry (if you haven't already):

.. code-block:: bash

    curl -sSL https://install.python-poetry.org | python3 -

2. Install LAPA-NG:

.. code-block:: bash

    pip install lapa-ng

Dependencies
-----------

LAPA-NG requires Python 3.10 or higher and the following main dependencies:

* click >= 8.1.8
* xlrd >= 2.0.1
* openpyxl >= 3.1.2
* lxml >= 5.4.0
* xlwt >= 1.3.0
* pandas >= 2.2.3
* cachetools >= 5.5.2
* pyyaml >= 6.0.2

These will be automatically installed when installing LAPA-NG.

Development Installation
-----------------------

To install LAPA-NG for development:

.. code-block:: bash

    git clone https://github.com/yourusername/lapa-ng.git
    cd lapa-ng
    poetry install

This will create a virtual environment and install all dependencies, including development dependencies.

To activate the virtual environment:

.. code-block:: bash

    poetry shell

Alternatively, you can run commands directly using poetry:

.. code-block:: bash

    poetry run python -m lapa_classic --help 