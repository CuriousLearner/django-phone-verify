How to write custom backend?
============================

You can write your own backend for any service of your choice, instead of ``Twilio`` and ``Nexmo``, which are already provided by ``django-phone-verify``.

**Note**: For this tutorial, we will consider writing backend for ``Nexmo``. The steps will remain same for any other service.

1. Create a file with any name within your project. Let's say ``nexmo.py``.

2. Define settings in your project's ``settings.py`` as

.. code-block:: python

    # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoBackend', # Path to the custom backend class which we will be creating in further steps
        'OPTIONS': {
            # define options required for your service
            'KEY': 'Fake Key',
            'SECRET': 'Fake secret',
            'FROM': '+1232328372987',
            'SANDBOX_TOKEN': '123456', # Optional for sandbox utility
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600  # In seconds only
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,  # If False, then a security code can be used multiple times for verification
    }

**Note**: You may use a client for your service(if available) to send sms or you may directly use the APIs for that service. Since, ``NEXMO`` has a client called ``nexmo``, we will be leveraging its functionality.

3. Create a class ``NexmoBackend`` within ``nexmo.py``. You must inherit your custom class with ``BaseBackend``.

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

4. Override ``send_sms`` method of ``BaseBackend`` class to implement functionality for sending sms. It must have two positional parameters ``number`` and ``message`` respectively.

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
        # Implement your service's send sms functionality
        self.client.send_message({
            'from': self._from,
            'to': number,
            'text': message,
        })

5. For sending bulk messages, you must override ``send_bulk_sms`` method of ``BaseBackend`` class. It must have two positional parameters ``numbers`` and ``message`` respectively.

.. code-block:: python

    ...

    def send_sms(self, number, message):
        # Implement your service's send sms functionality
        self.client.send_message({
            'from': self._from,
            'to': number,
            'text': message,
        })

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(self, number=number, message=message)

How to create custom Sandbox Service
------------------------------------

The above steps will remain same if you wish to create a sandbox utility for your service. We'll create a new class with keeping above steps in mind. Apart from it, we will need to override a few more methods and tweak our ``__init__`` method a bit.

1. Create a custom sandbox class for your service. Let's say ``NexmoSandboxBackend``. Again, it must inherit from ``BaseBackend``.

2. Define your class's constructor same as above. Just fetch ``SANDBOX_TOKEN`` from the settings as well. Also, override ``send_sms`` and ``send_bulk_sms`` for your service same as above.

.. code-block:: python

    # Third Party Stuff
    import nexmo
    from phone_verify.backends.base import BaseBackend


    class NexmoSandboxBackend(BaseBackend):

        def __init__(self, **options):
            super().__init__(**options)

            # Lower case it just to be sure
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key", None)
            self._secret = options.get("secret", None)
            self._from = options.get("from", None)
            self._token = options.get("sandbox_token", None) # Fetch sandbox token for your service.

            # Create a Nexmo Client object
            self.client = nexmo.Client(key=self._key, secret=self._secret)

        def send_sms(self, number, message):
            # Implement your service's send sms functionality
            self.client.send_message({
                'from': self._from,
                'to': number,
                'text': message,
            })

        def send_bulk_sms(self, numbers, message):
            for number in numbers:
                self.send_sms(self, number=number, message=message)

3. Override ``generate_security_code`` as defined below:

.. code-block:: python

    ...

    def generate_security_code(self):
        """
        Returns a fixed security code
        """
        return self._token

4. Override ``validate_security_code`` as defined below:

.. code-block:: python

    ...

    def generate_security_code(self):
        """
        Returns a fixed security code
        """
        return self._token

    def validate_security_code(self, security_code, phone_number, session_token):
        return self.SECURITY_CODE_VALID

It must have ``security_code``, ``phone_number`` and ``session_token`` as its positional parameters.

Now your Sandbox class is ready to be used. To use this class, give path to this class in your ``PHONE_VERIFY`` settings ``BACKEND`` key.

.. code-block:: python

   # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoSandboxBackend', # Path to the custom sandbox class
        'OPTIONS': {
            # define options required for your service
            'KEY': 'Fake Key',
            'SECRET': 'Fake secret',
            'FROM': '+1232328372987',
            'SANDBOX_TOKEN': '123456', # Optional for sandbox utility
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600  # In seconds only
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,  # If False, then a security code can be used multiple times for verification
    }
