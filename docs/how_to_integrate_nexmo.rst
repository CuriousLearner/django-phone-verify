How to integrate ``Nexmo``?
===========================

**Note**: ``django-phone-verify`` provides ``Nexmo`` as an additional service which can be used as the backend for its functioning.

To integrate ``Nexmo``, you will need to edit the ``PHONE_VERIFY`` settings within ``settings.py`` of your Django project.

Define your settings as:

.. code-block:: python

    # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.nexmo.NexmoBackend',
        'OPTIONS': {
            'KEY': 'fake',
            'SECRET': 'fake',
            'FROM': '+14755292729',
            'NEXMO_SANDBOX_TOKEN':'123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600  # In seconds only
    }

And that's it. Now you'll be able to use ``Nexmo`` as your main service for backend functioning of ``django-phone-verify``.
