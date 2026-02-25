"""
A2AS Security Boundaries (S principle)
Wraps external inputs in special tags to isolate untrusted content
"""


def wrap_tool_output(tool_name: str, output: str) -> str:
    """
    Wrap tool output in security boundaries

    S - Security Boundaries: Isolate untrusted tool responses
    """
    return f"[TOOL EXECUTED: {tool_name}]\n<a2as:tool:{tool_name}>\n{output}\n</a2as:tool:{tool_name}>\n[END OF TOOL OUTPUT]"


def wrap_user_input(user_message: str, signature: str = None) -> str:
    """
    Wrap user input in security boundaries with optional authentication

    S - Security Boundaries: Isolate untrusted input
    A - Authenticated Prompts: Include integrity hash
    """
    if signature:
        # Include first 8 chars of signature for authentication
        return f"<a2as:user:{signature[:8]}>\n{user_message}\n</a2as:user:{signature[:8]}>"
    else:
        return f"<a2as:user>\n{user_message}\n</a2as:user>"