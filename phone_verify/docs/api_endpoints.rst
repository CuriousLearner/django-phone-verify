Authentication
==============

Phone Registration
==================

Send security\_code on given phone\_number
------------------------------------------

::

    POST /api/phone/register

**NOTE**: Hit again for resending the security\_code.

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
        "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
    }

Verify if security\_code entered is correct
-------------------------------------------

::

    POST /api/phone/verify

**Parameters**

+-----------------+----------+------------------------------------------------+
| Name            | Type     | Description                                    |
+=================+==========+================================================+
| phone\_number   | string   | phone\_number of the user.                     |
+-----------------+----------+------------------------------------------------+
| security\_code  | string   | Security code (security_code) for the user     |
+-----------------+----------+------------------------------------------------+
| session\_token  | string   | iOS session token to verify the phone\_number  |
+-----------------+----------+------------------------------------------------+

**Request**

.. code:: json

    {
        "phone_number": "+9180765XXX10",
        "security_code": "711146",
        "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
    }

**Response**

::

    Status: 200 OK

.. code:: json

    {
        "message": "Security code is valid."
    }
