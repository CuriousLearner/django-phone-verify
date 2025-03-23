Getting Started
===============

Installation
------------

You can install ``django-phone-verify`` using ``pip``. The package supports optional extras
for different SMS backends:

.. code-block:: shell

    pip install django-phone-verify          # Core install (only if you want to write your own backend)
    pip install django-phone-verify[twilio]  # Twilio support
    pip install django-phone-verify[nexmo]   # Nexmo (Vonage) support
    pip install django-phone-verify[all]     # All supported backends


Configuration
-------------

1. **Add to ``INSTALLED_APPS``**

.. code-block:: python

    # settings.py

    INSTALLED_APPS = [
        ...
        'phone_verify',
        ...
    ]

2. **Configure settings**

.. code-block:: python

    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',  # or NexmoBackend
        'OPTIONS': {
            'SID': 'fake',
            'SECRET': 'fake',
            'FROM': '+14755292729',
            'SANDBOX_TOKEN': '123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': False,
    }

3. **Run migrations**

.. code-block:: shell

    python manage.py migrate

This creates the ``SMSVerification`` table to store phone numbers, session tokens, and security codes.


Next Steps
----------

- To integrate phone number verification into your user signup process, refer to the :doc:`integration` guide.
- To write your own SMS backend or sandbox logic, see :doc:`customization`.
