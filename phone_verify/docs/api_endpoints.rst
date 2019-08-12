Authentication
==============

Phone Registration
==================

Send OTP on given phone\_number
-------------------------------

::

    POST /api/phone/register

**NOTE**: Hit again for resending the OTP.

**Parameters**

+-----------------+----------+----------------------------------------------------------------------------------------------+
| Name            | Type     | Description                                                                                  |
+=================+==========+==============================================================================================+
| phone\_number   | string   | phone\_number of the user. (should contain the country extension as given in example call)   |
+-----------------+----------+----------------------------------------------------------------------------------------------+

**Example**

.. code:: json

    {
        "phone_number": "+9180765XXX10"
    }

**Response**

::

    Status: 200 OK

.. code:: json

    {
        "session_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
    }

Verify if OTP entered is correct
--------------------------------

::

    POST /api/phone/verify

**Parameters**

+-----------------+----------+------------------------------------------------+
| Name            | Type     | Description                                    |
+=================+==========+================================================+
| phone\_number   | string   | phone\_number of the user.                     |
+-----------------+----------+------------------------------------------------+
| otp             | string   | One-Time-Password (OTP) for the user           |
+-----------------+----------+------------------------------------------------+
| session\_code   | string   | iOS session code to verify the phone\_number   |
+-----------------+----------+------------------------------------------------+

**Request**

.. code:: json

    {
        "phone_number": "+9180765XXX10",
        "otp": "711146",
        "session_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
    }

**Response**

::

    Status: 200 OK

.. code:: json

    {
        "message": "OTP is valid."
    }

