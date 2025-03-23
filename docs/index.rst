Welcome to Django Phone Verify's Documentation!
===============================================

**Django Phone Verify** is a lightweight and flexible Django app that enables easy phone number verification via SMS.

It supports pluggable backends such as **Twilio** and **Nexmo (Vonage)**, and can be extended to work with any other SMS service.
Users receive a security code via SMS and verify their phone numbers by submitting that code to your API.

Whether you're building registration flows, login mechanisms, or two-factor authentication —
Django Phone Verify provides the core functionality so you can focus on your business logic.

.. important::

    This library supports optional extras for installation:

    - ``django-phone-verify[twilio]`` – for Twilio support
    - ``django-phone-verify[nexmo]`` – for Nexmo/Vonage support
    - ``django-phone-verify[all]`` – to install all supported backends

📚 Documentation Sections
-------------------------

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    getting_started
    integration
    customization
    contributing

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
