# Security Policy

## Supported Versions

We actively support the following versions of django-phone-verify with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take the security of django-phone-verify seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:

**sanyam@sanyamkhurana.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### What to Expect

After submitting a vulnerability report, you can expect:

1. **Acknowledgment**: We'll acknowledge receipt of your vulnerability report within 48 hours
2. **Assessment**: We'll investigate and assess the issue, keeping you updated on our progress
3. **Fix**: If confirmed, we'll work on a fix and coordinate a disclosure timeline with you
4. **Credit**: If you wish, we'll publicly credit you for the responsible disclosure

### Security Best Practices

When using django-phone-verify in production, we recommend:

1. **Rate Limiting**: Always implement rate limiting on verification endpoints to prevent:
   - Brute force attacks on security codes
   - SMS sending abuse
   - Cost-based DoS attacks

2. **Environment Variables**: Store sensitive credentials (Twilio/Nexmo keys) in environment variables, never in code

3. **HTTPS Only**: Always use HTTPS in production to protect session tokens and security codes in transit

4. **Token Expiration**: Set reasonable `SECURITY_CODE_EXPIRATION_TIME` values (recommended: 300-600 seconds)

5. **One-Time Codes**: Consider enabling `VERIFY_SECURITY_CODE_ONLY_ONCE: True` for high-security applications

6. **Input Validation**: Validate phone numbers on the client side before sending to prevent malformed requests

7. **Monitoring**: Monitor for unusual patterns like:
   - High SMS sending rates from single IPs
   - Multiple failed verification attempts
   - Verification attempts for many different phone numbers from one source

For more detailed security guidance, see our [Security Best Practices documentation](https://www.sanyamkhurana.com/django-phone-verify/security.html).

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported releases
4. Release new security update versions as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue to discuss.
