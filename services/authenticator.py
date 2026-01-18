import hashlib
import hmac
import os


PROMPT_SIGN_SECRET = os.getenv("PROMPT_SIGN_SECRET")


def sign_message(prompt):
    """Creates cryptographic sign for message"""
    return hmac.new(PROMPT_SIGN_SECRET.encode(), prompt.encode(), hashlib.sha256).hexdigest()[:16]


def verify_sign(prompt, signature):
    """Verifies cryptographic sign for message"""
    expected_signature = sign_message(prompt)
    return hmac.compare_digest(expected_signature, signature)
