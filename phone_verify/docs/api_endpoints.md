# Authentication

# Phone Registration

## Send OTP on given phone_number

```
POST /api/phone/register
```

__NOTE__: Hit again for resending the OTP.

__Parameters__

Name         | Type    | Description
-------------|---------|--------------------------------------
phone_number | string | phone_number of the user. (should contain the county extension as given in example call)


__Example__
```json
{
	"phone_number": "+9180765XXX10"
}
```

__Response__
```json
{
    "session_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
}
```

## Verify if OTP entered is correct

```
POST /api/phone/verify
```
**Parameters**

Name            | Type    |  Description
----------------|---------|---------------------------
phone_number    | string  | phone_number of the user.
otp             | string  | One-Time-Password (OTP) for the user
session_code    | string  | iOS session code to verify the phone_number

**Request**
```json
{
    "phone_number": "+9180765XXX10",
    "otp": "711146",
    "session_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
}
```

**Response**

```
Status: 200 OK
```

```json
{
    "message": "OTP is valid."
}
```
