from smolagents import ToolCallingAgent, PromptTemplates, FinalAnswerPromptTemplate, PlanningPromptTemplate

from models.email_agent_tools import EmailRegistry, FindEmailsTool, SendEmailTool
from . import model


def get_agent_with_a2as(user_addr: str, email_registry: EmailRegistry):
    return ToolCallingAgent(
        name="mailbox_agent_a2as",
        tools = [
            FindEmailsTool(user_addr, email_registry),
            SendEmailTool(user_addr, email_registry),
        ],
        model=model,
        max_steps=5,
    )
