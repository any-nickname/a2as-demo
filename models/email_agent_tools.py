from models.email_list import EmailList
from typing import Dict
from smolagents import Tool


class EmailRegistry():
    def __init__(self, emails: Dict[str, EmailList]):
        self.registry = emails
    
    def __getitem__(self, key: str) -> EmailList:
        return self.registry[key]


class FindEmailsTool(Tool):
    name = "find_emails"
    description = (
        "Search for emails based on keywords in an email list of current user."
        "Input should be a search query string and the email list to search in." \
        "If you want to see all emails, just use the query 'all emails'."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant emails",
        },
    }
    output_type = "string"

    def __init__(self, user_address: str, registry: EmailRegistry):
        super().__init__()
        self.email_address = user_address
        self.email_registry = registry

    def forward(self, query: str) -> str:
        results = self.email_registry[self.email_address].keyword_search(query, top_k=15)

        if not results:
            return f"No emails found in the email list matching your query."
        
        output = f"Found {len(results)} email(s) in the email list:\n\n"
        for i, email in enumerate(results, 1):
            output += f"Email {i}:\n"
            output += f"From: {email['from']}\n"
            output += f"To: {email['to']}\n"
            output += f"Subject: {email['subject']}\n"
            output += f"Body: {email['body']}\n\n"

        return output
    

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

    def __init__(self, user_address: str, registry: EmailRegistry):
        super().__init__()
        self.email_address = user_address
        self.email_registry = registry


    def forward(self, to_address: str, subject: str, body: str) -> str:
        self.email_registry[self.email_address].add_sent_email(to_address, subject, body)
        self.email_registry[to_address].add_received_email(self.email_address, subject, body)
        return f"Email sent successfully!\nFrom: {self.email_address}\nTo: {to_address}\nSubject: {subject}\nBody:{body}"