Release Notes
-------------

[Dev]
^^^^^

Added
"""""
- Optional dependencies (``twilio``, ``nexmo``) are now only required if explicitly used in the ``PHONE_VERIFICATION["BACKEND"]`` setting.
- Improved error messaging to guide users to install the required backend package (e.g., ``twilio``, ``nexmo``) only when needed.
- Custom backends now raise a clear ``RuntimeError`` if the import fails, instead of misleading dependency errors.
- Support for Python 3.11, 3.12, 3.13
- CI tests for Py{311,312,313}-Django{2x,3x,4x,5x}.

[3.0.0]
^^^^^^^

Added
"""""
- Support for Django 4.x.
- Support for Django 3.2.

Changed
"""""""
- Method ``phone_verify.backends.nexmo.NexmoBackend.send_sms`` changes parameter name from ``numbers`` to ``number`` to be consistent with rest of the inherited classes.

[2.0.1]
^^^^^^^

Added
"""""
- Support for Python 3.8 & Python 3.9.
- CI tests for Py{36,37,38,39}-Django{20,21,22,30,31}.

Changed
"""""""
- Fixed issue ``generate_session_token`` to handle cases in Py38, Py39 when the ``session_token`` is already ``string`` instead of ``bytes``.

[2.0.0]
^^^^^^^

**NOTE**: The previous version of this library provided the ``security_code`` in the JWT ``session_token``. You would have to re-verify ``phone_numbers`` in *this* version to ensure they are authentically verified.

Added
"""""

- Tests added to provide 100% coverage on the package.
- Add ``nexmo.errors.ClientError`` as exception class in ``phone_verify.backends.nexmo.NexmoBackend`` & ``phone_verify.backends.nexmo.NexmoSandboxBackend``.

Changed
"""""""

- Method signature changed for ``phone_verify.backends.BaseBackend.generate_session_token``. It now accepts only ``phone_number`` instead of combination of ``phone_number`` and ``security_code``.
- Remove the ``security_code`` from JWT ``session_token`` to avoid leaking information.
- Add nonce in ``session_token`` to generate unique tokens for each ``phone_number``.
- Fixes call to ``phone_verify.backends.nexmo.NexmoBackend.send_sms`` method.

[1.1.0]
^^^^^^^

Added
"""""

- Support ``Nexmo`` as a backend service along with ``Twilio``.
- Add docs for writing a custom backend.

Changed
"""""""

- Update ``backends.base.BaseBackend.validate_security_code`` to use ``save()`` instead of ``update()`` to allow Django to emit its ``post_save()`` signal.

[1.0.0]
^^^^^^^

Added
"""""

- Add coverage report through ``coveralls``.
- Support for One-Time Passwords (OTP) using ``VERIFY_SECURITY_CODE_ONLY_ONCE`` as ``True`` in the settings.
- Script to support makemigrations for development.
- ``BaseBackend`` status now have ``SECURITY_CODE_VERIFIED`` and ``SESSION_TOKEN_INVALID`` status to support new states.

Changed
"""""""

- Rename ``TWILIO_SANDBOX_TOKEN`` to ``SANDBOX_TOKEN``.
- Fix signature for ``send_bulk_sms`` method in ``TwilioBackend`` and ``TwilioSandboxBackend``.
- Response for ``/api/phone/register`` contains key ``session_token`` instead of ``session_code``.
- Request payload for ``/api/phone/verify`` now expects ``session_token`` key instead of ``session_code``.
- Response for ``/api/phone/verify`` now sends additional response of ``Security code is already verified`` in case ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is set to ``True``.
- Rename ``otp`` to ``security_code`` in code and docs to be more consistent.
- Rename ``BaseBackend`` status from ``VALID``, ``INVALID``, ``EXPIRED`` to ``SECURITY_CODE_VALID``, ``SECURITY_CODE_INVALID``, and ``SECURITY_CODE_EXPIRED`` respectively.
- Rename ``session_code`` to ``session_token`` to be consistent in code and naming across the app.
- Rename service ``send_otp_and_generate_session_code`` to ``send_security_code_and_generate_session_token``.
- Rename method ``BaseBackend.generate_token`` to ``BaseBackend.generate_security_code``.
- Rename method ``create_otp_and_session_token`` to ``create_security_code_and_session_token``.
- Rename method ``BaseBackend.validate_token`` to ``BaseBackend.validate_security_code`` with an additional parameter of ``session_token``.

[0.2.0]
^^^^^^^

Added
"""""

- ``pre-commit-config`` to maintain code quality using black and other useful tools.
- Docs for integration and usage in `getting_started.rst`_.
- Tox for testing on `py{37}-django{20,21,22}`.
- Travis CI for testing builds.

Changed
"""""""

- Convert ``*.md`` docs to reST Markup.
- Fix issue with installing required package dependencies via ``install_requires``.

[0.1.1]
^^^^^^^

Added
"""""

- README and documentation of API endpoints.
- ``setup.cfg`` to manage coverage.
- ``phone_verify`` app including backends, requirements, tests.
- Initial app setup.
