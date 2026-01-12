from smolagents import ToolCallingAgent

from models.behavior_certificates import EmailBehaviorCertificates
from models.email_agent_tools import EmailRegistry, FindEmailsTool, SendEmailTool
from . import model


def get_agent_with_a2as(user_addr: str, email_registry: EmailRegistry):
    behavior_certificates = EmailBehaviorCertificates()

    return ToolCallingAgent(
        name="mailbox_agent_a2as",
        tools = [
            # For protected agent we use real email behavior certificates.
            FindEmailsTool(user_addr, email_registry, behavior_certificates),
            SendEmailTool(user_addr, email_registry, behavior_certificates),
        ],
        model=model,
        max_steps=5,
    )
