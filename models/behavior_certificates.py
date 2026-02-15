"""
Behavior Certificate is the 1st letter of BASIC abbreviation and one of the principles of A2AS framework.

Here we implement this principle through access-check,
which is being called in the tools which are used by our llm-agent.

We have two types of behavior:
- dummy behavior, where everything is allowed (for mode where A2AS is disabled)
- protected behavior, where real checks take place (for mode when A2AS is enabled)
"""
from typing import Protocol
import re


class BehaviorCertificates(Protocol):
    """Interface for everything that is used as behavior certificates"""

    def check_right_to_find_emails(self) -> tuple[bool, str]:
        ...

    def check_right_to_send_email(self, to_addr: str, subject: str, body: str) -> tuple[bool, str]:
        ...


class DummyEmailBehaviorCertificates:
    """Dummy behavior certificate class, which never prohibits anything"""

    def check_right_to_find_emails(self) -> tuple[bool, str]:
        return True, ""

    def check_right_to_send_email(self, to_addr: str, subject: str, body: str) -> tuple[bool, str]:
        return True, "You are authorized to send any emails"


class EmailBehaviorCertificates:
    """Email behavior certificate class that verifies the right to perform certain actions"""

    def check_right_to_find_emails(self) -> tuple[bool, str]:
        return True, ""

    def check_right_to_send_email(self, to_addr: str, subject: str, body: str) -> tuple[bool, str]:
        # 1. Check, that email is being sent only to corporate emails, end with "@goodcorp.ai".
        if not to_addr.endswith("@goodcorp.ai"):
            return False, "Sending emails to non-corporate addresses is prohibited"

        # 2. Check that subject does not contain "Confidential" or "Corporate" label.
        if "confidential" in subject.lower() or "corporate" in subject.lower():
            return False, "You can't send this email because it has label \"Confidential\" or \"Corporate\" in its subject"

        # 3. Check that body does not contain string token and token pattern
        if 'token' in body and re.findall(r"\d{3}-\d{2}", body):
            return False, "You can't send this email because it contains token data, which is sensitive information"

        return True, ""