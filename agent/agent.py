from smolagents import ToolCallingAgent

from models.behavior_certificates import DummyEmailBehaviorCertificates
from models.email_agent_tools import EmailRegistry, FindEmailsTool, SendEmailTool
from . import model


def get_agent(user_addr: str, email_registry: EmailRegistry):
    behavior_certificates = DummyEmailBehaviorCertificates()

    return ToolCallingAgent(
        name='mailbox_agent',
        tools = [
            # For unprotected email agent we use DummyEmailBehaviorCertificates.
            FindEmailsTool(user_addr, email_registry, behavior_certificates),
            SendEmailTool(user_addr, email_registry, behavior_certificates),
        ],
        model=model,
        max_steps=5,
    )
