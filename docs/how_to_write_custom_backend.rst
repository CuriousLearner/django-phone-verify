How to write custom backend?
============================

In case you want to use anything other than the provided backends (``phone_verify.backends.nexmo.NexmoBackend`` and ``phone_verify.backends.twilio.TwilioBackend``), you can write a custom backend by extending ``phone_verify.backends.base.BaseBackend`` as shown below.

**Note**: For this tutorial, we will consider writing backend for ``Nexmo``. The steps will remain same for any other service.

1. Create a file with any name within your project. Let's say ``nexmo.py``.

2. Define settings in your project's ``settings.py`` as

.. code-block:: python

    # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoBackend',  # Path to the custom backend class which we will be creating in further steps
        'OPTIONS': {
            # define options required for your service
            'KEY': 'Fake Key',
            'SECRET': 'Fake secret',
            'FROM': '+1232328372987',
            'SANDBOX_TOKEN': '123456',  # Optional for sandbox utility
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600  # In seconds only
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,  # If False, then a security code can be used multiple times for verification
    }

**Note**: You may use a client for your service(if available) to send SMS or you may directly use the APIs for that service. Since, ``Nexmo`` has a client called ``nexmo``, we will be leveraging its functionality.

3. Create a class ``NexmoBackend`` within ``nexmo.py``. You must inherit your custom class with ``phone_verify.backends.base.BaseBackend``.

.. code-block:: python

    # Third Party Stuff
    import nexmo
    from phone_verify.backends.base import BaseBackend


    class NexmoBackend(BaseBackend):

        def __init__(self, **options):
            super().__init__(**options)

            # Lower case it just to be sure
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key", None)
            self._secret = options.get("secret", None)
            self._from = options.get("from", None)

            # Create a Nexmo Client object
            self.client = nexmo.Client(key=self._key, secret=self._secret)

Initialize your class constructor with ``options`` dictionary which contains all the settings specific to your service defined in ``settings.py``. We have fetched each setting from ``options`` in above piece of code. Apart from it, we have created a client for our service by providing it the necessary settings.

4. Override ``send_sms`` method of ``phone_verify.backends.base.BaseBackend`` class to implement functionality for sending SMS. It must have two positional parameters ``number`` and ``message`` respectively.

.. code-block:: python

    ...

    def __init__(self, **options):
        super().__init__(**options)

        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._key = options.get("key", None)
        self._secret = options.get("secret", None)
        self._from = options.get("from", None)

        # Create a Nexmo Client object
        self.client = nexmo.Client(key=self._key, secret=self._secret)

    def send_sms(self, number, message):
        # Implement your service's SMS sending functionality
        self.client.send_message({
            'from': self._from,
            'to': number,
            'text': message,
        })

5. For sending bulk messages, you must override ``send_bulk_sms`` method of ``phone_verify.backends.base.BaseBackend`` class. It must have two positional parameters ``numbers`` and ``message`` respectively.

.. code-block:: python

    ...

    def send_sms(self, number, message):
        # Implement your service's SMS sending functionality
        self.client.send_message({
            'from': self._from,
            'to': number,
            'text': message,
        })

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(self, number=number, message=message)

How to create custom Sandbox Service?
-------------------------------------

The above steps will remain same if you wish to create a sandbox utility for your service. We'll create a new class with keeping above steps in mind. Apart from it, we will need to override a few more methods and tweak our ``__init__`` method a bit.

1. Create a custom sandbox class for your service, ``NexmoSandboxBackend`` inherited from ``phone_verify.backends.base.BaseBackend``.

2. The constructor for your sandbox environment can get the ``SANDBOX_TOKEN`` from settings as shown. This enables you to keep the token constant for testing purposes. You can then override ``send_sms`` and ``send_bulk_sms`` for the service as done in case of creating actual custom backend.

.. code-block:: python

    # Third Party Stuff
    import nexmo
    from phone_verify.backends.base import BaseBackend
    from phone_verify.models import SMSVerification


    class NexmoSandboxBackend(BaseBackend):

        def __init__(self, **options):
            super().__init__(**options)

            # Lower case it just to be sure
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key", None)
            self._secret = options.get("secret", None)
            self._from = options.get("from", None)
            self._token = options.get("sandbox_token", None)  # Fetch sandbox token for your service.

            # Create a Nexmo Client object
            self.client = nexmo.Client(key=self._key, secret=self._secret)

        def send_sms(self, number, message):
            # Implement your service's SMS sending functionality
            self.client.send_message({
                'from': self._from,
                'to': number,
                'text': message,
            })

        def send_bulk_sms(self, numbers, message):
            for number in numbers:
                self.send_sms(self, number=number, message=message)

        def generate_security_code(self):
            """
            Returns a fixed security code
            """
            return self._token

        def validate_security_code(self, security_code, phone_number, session_token):
            """
            Always validate security code for testing purposes
            """
            return SMSVerification.objects.none(), self.SECURITY_CODE_VALID

We have also overriden the ``generate_security_code`` and ``validate_security_code`` methods of ``BaseBackend`` class. The ``validate_security_code`` method must have ``security_code``, ``phone_number`` and ``session_token`` as its positional parameters. We returned an empty SMSVerification object to keep the return arguments uniform with the acutal base class method.

In order to use this new custom backend class, it should be replaced in the ``BACKEND`` key under ``PHONE_VERIFICATION`` settings as shown below.

.. code-block:: python

   # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoSandboxBackend',  # Path to the custom sandbox class
        'OPTIONS': {
            # define options required for your service
            'KEY': 'Fake Key',
            'SECRET': 'Fake secret',
            'FROM': '+1232328372987',
            'SANDBOX_TOKEN': '123456',  # Optional for sandbox utility
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600  # In seconds only
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,  # If False, then a security code can be used multiple times for verification
    }
