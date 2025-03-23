Contributing
============

Thank you for your interest in contributing to ``django-phone-verify``!
The following guide will help you set up your development environment and start contributing effectively.

Project Setup
-------------

1. **Clone the repository**

   Clone the GitHub repository to your local system:

   .. code-block:: shell

       git clone https://github.com/CuriousLearner/django-phone-verify.git

2. **Create and activate a virtual environment**

   You may use any tool of your choice (e.g., ``venv`` or ``virtualenv``). Here’s how to do it using the built-in ``venv``:

   .. code-block:: shell

       python3 -m venv venv
       source venv/bin/activate

3. **Install development dependencies**

   Make sure you are in the root directory of the project, then install the required dependencies:

   .. code-block:: shell

       python -m pip install -r requirements/development.txt

You now have a local setup of ``django-phone-verify`` ready for development and contribution.

.. _running-tests:

Running Tests
-------------

Unit tests are located in the ``tests/`` directory, and the project uses ``pytest`` for testing.

1. **Install testing dependencies**

   From the root directory, run:

   .. code-block:: shell

       python -m pip install -r requirements/testing.txt

2. **Run the test suite**

   To execute the test suite:

   .. code-block:: shell

       pytest

3. **Run tests with code coverage**

   For checking code coverage, use the ``--cov`` option:

   .. code-block:: shell

       pytest --cov

4. **Test with multiple Python/Django versions using tox**

   The project supports multiple versions of Python and Django. To run the full test matrix using ``tox``, use:

   .. code-block:: shell

       tox

   Refer to the ``tox.ini`` file at the root of the repository for supported versions and configurations.

Local Development and Testing
-----------------------------

After making code changes, you can install the app in **editable mode** inside your Django project to test your modifications:

.. code-block:: shell

    cd /path/to/your/django/project
    pip install -e /path/to/local/django-phone-verify

This installs your local copy instead of the one from PyPI, allowing you to test changes immediately.

Once you're satisfied, refer back to the :ref:`running-tests` section to verify that everything works correctly before submitting a pull request.

----

Feel free to open issues, suggest improvements, and submit pull requests. Happy coding!
