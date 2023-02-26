Contributing
============

Thank you for your interest in contributing to this project. The following set of steps should help you get started with contributing to ``django-phone-verify``.

Project Setup
-------------

1. Clone the git repository for this project onto your local system.

::

    git clone https://github.com/CuriousLearner/django-phone-verify.git

2. Create a virtual environment. You may use any tool of your choice.

::

    $ python3 -m venv venv

Activate env using

::

    $ source venv/bin/activate

3. Install the python dependencies via the following command. Make sure you are in the root directory.

::

    (venv) $ python -m pip install -r requirements/development.txt

That's it! You now have a local setup of ``django-phone-verify``. You can start contributing to it.


Running Tests
-------------

``django-phone-verify`` has unit tests located in the ``tests/`` directory. The project uses ``pytest`` to write and run the tests.

Before we proceed with performing tests, we should install the testing dependencies. Install the testing requirements via the following command. Make sure you are in the root directory.

::

    (venv) $ python -m pip install requirements/testing.txt

To run the test, you have to run the ``pytest`` command. If you want to get the code coverage, use the ``--cov`` argument as

::

    (venv) $ pytest --cov

This will list down the current code coverage.

To test your changes with different versions of Python & Django that the project supports, you can use ``tox`` like:

::

    (venv) $ tox

This would run all the tests with a combination of all Python/Django versions that it supports. Check the ``tox.ini`` file at the root of the project for more details.

Local Development and testing
-----------------------------

Once you've made code changes, you can install this local development copy of the Django app in your project by using the ``-e`` flag with ``pip install`` in the following manner:

::

    $ cd /path/to/new/django/project
    $ pip install -e /path/to/local/django-phone-verify

This will install your local modified copy of the app in your Django application rather than fetching it from PyPI. After you're satisfied with the changes, you can run tests using the `running tests <#running-tests>`_ section above.
