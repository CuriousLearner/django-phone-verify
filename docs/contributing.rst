Thank you for your interest in contributing to this project. The following set of steps should help you get started with contributing to ``django-phone-verfy``.

Project Setup
=============

1. Clone the git repository for this project onto your local system.

::

    git clone https://github.com/CuriousLearner/django-phone-verify.git

2. Create a virtual environment. You may use any tool of your choice.

3. Install the python dependencies via the following command. Make sure you are in the root directory.

::

    python -m pip install -r requirements/development.txt

That's it! You now have a local setup of ``django-phone-verify``. You can start contributing to it.


Tests
=====

``django-phone-verify`` has unit tests located in the ``tests/`` dir. The project uses ``pytest`` to write and run the tests.

Before we proceed with performing tests, we should install the testing dependencies. Install the testing requirements via the following command. Make sure you are in the root directory.

::

    python -m pip install requirements/testing.txt

To run the test, you have to run the ``pytest`` command. If you want to get the code coverage, use the ``--cov`` argument as

::

    pytest --cov

This will list down the current code coverage.
