# -*- coding: utf-8 -*-
BACKEND_SERVICES = [
    ("phone_verify.backends.twilio.TwilioBackend", "twilio.rest.Client"),
    ('phone_verify.backends.kavenegar.KavenegarBackend', "kavenegar.KavenegarAPI")
]
