Welcome to Django Phone Verify!
================================

**Secure phone number verification for Django applications**

``django-phone-verify`` is a production-ready Django library that provides phone number verification via SMS.
Whether you're building user registration, two-factor authentication, account recovery, or any feature requiring
phone verification, this library handles the complexity so you can focus on your application.

Why Django Phone Verify?
-------------------------

✅ **Production-Ready** - Used in production by companies worldwide, battle-tested and secure

✅ **Easy Integration** - Works with Django REST Framework or standard Django views

✅ **Flexible** - Supports Twilio, Nexmo/Vonage, or write your own backend for any SMS provider

✅ **Secure by Design** - JWT session tokens, configurable expiration, one-time codes, rate limiting support

✅ **Well Documented** - Comprehensive documentation with real-world examples

Quick Example
-------------

.. code-block:: python

    from phone_verify.services import send_security_code_and_generate_session_token
    from phone_verify.services import verify_security_code

    # Send verification code via SMS
    session_token = send_security_code_and_generate_session_token("+1234567890")

    # User receives SMS: "Your verification code is 847291"

    # Verify the code
    verify_security_code("+1234567890", "847291", session_token)
    # Returns: SECURITY_CODE_VALID

That's it! Phone verification in 3 lines of code.

Installation
------------

.. code-block:: shell

    # For Twilio users
    pip install django-phone-verify[twilio]

    # For Nexmo/Vonage users
    pip install django-phone-verify[nexmo]

    # Install all backends
    pip install django-phone-verify[all]

See :doc:`getting_started` for complete installation and configuration instructions.

📚 Documentation Sections
-------------------------

New to django-phone-verify? Start here!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 2

    getting_started
    integration
    configuration

Essential Guides
^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 2

    architecture
    security
    faq

Advanced Usage
^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 2

    advanced_examples
    customization

Reference & Help
^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 2

    api_reference
    troubleshooting
    changelog
    contributing

Common Use Cases
----------------

Choose your use case to see a complete implementation:

📱 **User Registration** - Verify phone numbers during signup
    See the integration examples in :doc:`integration`

🔐 **Two-Factor Authentication (2FA)** - Add SMS-based 2FA to login
    Complete example in :doc:`advanced_examples`

🔑 **Password Reset** - Allow users to reset passwords via SMS
    Step-by-step guide in :doc:`advanced_examples`

📧 **Marketing Opt-In** - Verify phone numbers for SMS marketing
    Implementation in :doc:`advanced_examples`

📞 **Phone Number Updates** - Securely update user phone numbers
    Secure flow in :doc:`advanced_examples`

Features at a Glance
--------------------

**Security**

- JWT-based session tokens prevent tampering
- Configurable code expiration (recommended: 5-10 minutes)
- One-time code usage option
- Rate limiting support to prevent abuse
- GDPR/CCPA compliance guidance

**Integration**

- Works with Django REST Framework (pre-built viewsets)
- Works with standard Django views and forms
- Compatible with any ``AUTH_USER_MODEL``
- No changes required to your user model

**SMS Providers**

- **Twilio** - Built-in support via ``TwilioBackend``
- **Nexmo/Vonage** - Built-in support via ``NexmoBackend``
- **Custom** - Write backends for AWS SNS, MessageBird, Plivo, etc.
- **Sandbox mode** - Test without sending real SMS

**Customization**

- Custom message templates with dynamic content
- Configurable security code length
- Custom validation logic
- Async/Celery support for better performance
- Multi-backend support (fallback providers)

Requirements
------------

- Python 3.8+
- Django 2.1+
- Django REST Framework 3.9+ (optional, for API endpoints)
- Twilio or Nexmo account (for production SMS)

Getting Help
------------

If you're stuck or have questions:

1. **Check the FAQ** - :doc:`faq` answers common questions
2. **Read Troubleshooting** - :doc:`troubleshooting` covers common issues
3. **Review Examples** - :doc:`advanced_examples` has real-world implementations
4. **Check API Docs** - :doc:`api_reference` for detailed API information
5. **Open an Issue** - `GitHub Issues <https://github.com/CuriousLearner/django-phone-verify/issues>`_
6. **Security Issues** - See our `Security Policy <https://github.com/CuriousLearner/django-phone-verify/security/policy>`_

Contributing
------------

We welcome contributions! Whether it's bug reports, feature requests, documentation improvements, or code:

- 🐛 `Report bugs <https://github.com/CuriousLearner/django-phone-verify/issues>`_
- 💡 Suggest features or improvements
- 📖 Improve documentation
- 🔧 Submit pull requests

See :doc:`contributing` for guidelines.

License
-------

``django-phone-verify`` is licensed under the **GNU General Public License v3 (GPLv3)**.

See the `LICENSE file <https://github.com/CuriousLearner/django-phone-verify/blob/master/LICENSE>`_ for details.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
