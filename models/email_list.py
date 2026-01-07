from typing import List, Dict
import json
import re


class EmailList:
    def __init__(self, user_address: str):
        self.user_address = user_address
        self.sent_emails: List[Dict[str, str]] = []
        self.received_emails: List[Dict[str, str]] = []


    def load_from_jsonl(self, filepath: str):
        """Load emails from JSONL file"""
        try:
            with open(filepath, "r") as f:
                for line in f:
                    if line.strip():
                        email = json.loads(line)
                        self.received_emails.append(email)
        except FileNotFoundError:
            print(f"File {filepath} not found. Using empty email list.")


    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """Simple keyword-based search"""
        query_lower = query.lower()

        if query_lower == 'all' or query_lower == 'all emails':
            return self.sent_emails + self.received_emails

        keywords = re.findall(r"\w+", query_lower)

        scored_emails = []
        for email in self.sent_emails + self.received_emails:
            text = f"{email.get('from', '')} {email.get('subject', '')} {email.get('body', '')}"
            score = sum(text.count(keyword) for keyword in keywords)
            if score > 0:
                scored_emails.append((score, email))

        scored_emails.sort(reverse=True, key=lambda x: x[0])
        return [email for _, email in scored_emails[:top_k]]
    

    def add_sent_email(self, to_addr: str, subject: str, body: str):
        """Add sent email to the sent list"""
        email = {"from": self.user_address, "to": to_addr, "subject": subject, "body": body}
        self.sent_emails.append(email)
        return email
    

    def get_sent_emails(self) -> List[Dict[str, str]]:
        """Get all sent emails"""
        return self.sent_emails


    def add_received_email(self, from_addr: str, subject: str, body: str):
        """Add a received email to the email list"""
        email = {"from": from_addr, "to": self.user_address, "subject": subject, "body": body}
        self.received_emails.append(email)
        return email


    def get_received_emails(self) -> List[Dict[str, str]]:
        """Get all received emails"""
        return self.received_emails