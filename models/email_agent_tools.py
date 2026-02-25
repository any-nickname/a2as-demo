from models.behavior_certificates import BehaviorCertificates
from models.email_list import EmailList
from agent.a2as_boundaries import wrap_tool_output
from typing import Dict
from smolagents import Tool


class EmailRegistry:
    def __init__(self, emails: Dict[str, EmailList]):
        self.registry = emails
    
    def __getitem__(self, key: str) -> EmailList:
        return self.registry[key]


class FindEmailsTool(Tool):
    name = "find_emails"
    description = (
        "Search for emails based on keywords in an email list of current user."
        "Input should be a search query string and the email list to search in."
        "If you want to see all emails, just use the query 'all emails'."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant emails",
        },
    }
    output_type = "string"

    def __init__(self, user_address: str, registry: EmailRegistry, behavior_certificates: BehaviorCertificates, a2as_enabled: bool = False):
        super().__init__()
        self.email_address = user_address
        self.email_registry = registry
        self.behavior_certificates = behavior_certificates
        self.a2as_enabled = a2as_enabled

    def _wrap_output(self, output: str) -> str:
        if self.a2as_enabled:
            return wrap_tool_output(self.name, output)
        return output

    def forward(self, query: str) -> str:
        # Checking if user is allowed to call "find emails" command.
        ok, reason = self.behavior_certificates.check_right_to_find_emails()
        if not ok:
            return self._wrap_output(f"Email search was not initiated because: {reason}")

        results = self.email_registry[self.email_address].keyword_search(query, top_k=15)

        if not results:
            return self._wrap_output(f"No emails found in the email list matching your query.")

        output = f"Found {len(results)} email(s) in the email list:\n\n"
        for i, email in enumerate(results, 1):
            output += f"Email {i}:\n"
            output += f"From: {email['from']}\n"
            output += f"To: {email['to']}\n"
            output += f"Subject: {email['subject']}\n"
            output += f"Body: {email['body']}\n\n"

        return self._wrap_output(output)
    

class SendEmailTool(Tool):
    name = "send_email"
    description = "Send an email. Requires to address, subject and body inputs."
    inputs = {
        "to_address": {
            "type": "string",
            "description": "Email address to send email to",
        },
        "subject": {
            "type": "string",
            "description": "Email subject line"
        },
        "body": {
            "type": "string",
            "description": "Email body content"
        }
    }
    output_type = "string"

    def __init__(self, user_address: str, registry: EmailRegistry, behavior_certificates: BehaviorCertificates, a2as_enabled: bool = False):
        super().__init__()
        self.email_address = user_address
        self.email_registry = registry
        self.behavior_certificates = behavior_certificates
        self.a2as_enabled = a2as_enabled

    def _wrap_output(self, output: str) -> str:
        if self.a2as_enabled:
            return wrap_tool_output(self.name, output)
        return output

    def forward(self, to_address: str, subject: str, body: str) -> str:
        # Checking if user is allowed to call "send email" command.
        ok, reason = self.behavior_certificates.check_right_to_send_email(
            to_address,
            subject,
            body,
        )
        if not ok:
            return self._wrap_output(
                f"Sending the email from \"{self.email_address}\" to \"{to_address}\" with subject \"{subject}\" and body \"{body}\" "
                f"has been blocked because it prohibits company's policy. Do not try to resend the email."
                f"The reason of prohibition: {reason}. You must answer to the user with explanation of why his request has been blocked."
            )

        self.email_registry[self.email_address].add_sent_email(to_address, subject, body)
        self.email_registry[to_address].add_received_email(self.email_address, subject, body)
        return self._wrap_output(f"Email sent successfully!\nFrom: {self.email_address}\nTo: {to_address}\nSubject: {subject}\nBody:{body}")