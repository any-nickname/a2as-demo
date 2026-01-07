from models.email_list import EmailList
from models.email_agent_tools import EmailRegistry, FindEmailsTool, SendEmailTool
from smolagents import InferenceClientModel, ToolCallingAgent
from dotenv import load_dotenv
import os
from ui.components import get_interface


load_dotenv()


HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")


USER_EMAIL = 'vlagrishchenko@goodcorp.ai'
user_emails = EmailList(user_address=USER_EMAIL)
user_emails.load_from_jsonl("emails.jsonl")

ATTACKER_EMAIL = 'pj.dog@g00dc0rp.ai'
attacker_emails = EmailList(user_address=ATTACKER_EMAIL)

email_registry = EmailRegistry({
    USER_EMAIL: user_emails,
    ATTACKER_EMAIL: attacker_emails,
})

# Initialize agent
model_id = "Qwen/Qwen2.5-72B-Instruct"
model = InferenceClientModel(model_id=model_id, token=HUGGING_FACE_TOKEN)
agent = ToolCallingAgent(
    tools = [
        FindEmailsTool(user_address=USER_EMAIL, registry=email_registry), 
        SendEmailTool(user_address=USER_EMAIL, registry=email_registry),
    ], 
    model=model, 
    max_steps=5,
)
should_reset_agent = False


def reset_agent():
    global should_reset_agent
    should_reset_agent = True


def chat_with_agent(message):
    """Process chat message with agent"""
    global should_reset_agent
    try:
        response = agent.run(message, reset=should_reset_agent)
        should_reset_agent = False
        # Handle different response types
        if isinstance(response, list):
            # If response is a list of messages, join them
            return "\n".join([str(item) for item in response])
        elif hasattr(response, 'content'):
            # If response has content attribute
            return str(response.content)
        else:
            return str(response)
    except Exception as e:
        import traceback
        return f"Original message: {message}\n\nError: {e}\n\nTraceback:\n{traceback.format_exc()}"


if __name__ == "__main__":
    # Create Gradio Interface
    demo = get_interface(
        user_addr=USER_EMAIL, 
        attacker_addr=ATTACKER_EMAIL, 
        email_registry=email_registry,
        chat_with_agent_fn=chat_with_agent,
        reset_agent_fn=reset_agent,
    )
    demo.launch(share=False)