import gradio as gr

from models.email_agent_tools import EmailRegistry
from ui.formatters import format_emails_list


def get_received_emails(addr: str, email_registry: EmailRegistry):
    """Get all received emails for the addr"""
    return format_emails_list(email_registry[addr].get_received_emails())


def get_sent_emails(addr: str, email_registry: EmailRegistry):
    """Get all sent emails from the addr"""
    return format_emails_list(email_registry[addr].get_sent_emails())


def send_email(
        from_addr: str, 
        to_addr: str, 
        subject: str, 
        body: str,
        email_registry: EmailRegistry,
):
    """Send email from from_addr to to_addr"""
    if not subject or not body:
        return "Error: Subject and body are required", get_received_emails(to_addr, email_registry), get_sent_emails(from_addr, email_registry)
        
    email_registry[from_addr].add_sent_email(to_addr, subject, body)
    email_registry[to_addr].add_received_email(from_addr, subject, body)

    return "✅ Email sent successfully!", get_received_emails(to_addr, email_registry), get_sent_emails(from_addr, email_registry)


def refresh_emails(user_addr: str, attacker_addr: str, email_registry: EmailRegistry):
    """Refresh all email displays"""
    return (
        get_received_emails(user_addr, email_registry), 
        get_sent_emails(user_addr, email_registry), 
        get_sent_emails(attacker_addr, email_registry),
        get_received_emails(attacker_addr, email_registry),
    )


def get_interface(
        user_addr: str,
        attacker_addr: str,
        email_registry: EmailRegistry,
        chat_with_agent_fn,
        reset_agent_fn,
):
    """Get Gradio interface for email agent demo"""

    # Custom CSS for toggle switch and visual changes
    custom_css = """
    #agent-wrapper {
        padding: 10px;
        transition: all 0.3s ease;
        border: 2px solid lightgray;
        border-radius: 8px;
    }
    
    .protected-mode {
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
    }

    #a2as-toggle-radio {
        display: flex !important;
        justify-content: center !important;
        margin: 15px 0 !important;
    }

    #a2as-toggle-radio .wrap {
        display: flex !important;
        gap: 0 !important;
        overflow: hidden !important;
    }

    #a2as-toggle-radio label {
        flex: 1;
        white-space: nowrap;
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        cursor: pointer;
        border: 1px solid gray;
        margin: 0;
        padding: 6px 80px;
        transition: all 0.2s ease-in-out;
    }
    
    #a2as-toggle-radio label:first-child {
        border-radius: 6px 0 0 6px;
    }
    
    #a2as-toggle-radio label:last-child {
        border-radius: 0 6px 6px 0;
    }

    #a2as-toggle-radio input[type="radio"] {
        display: none !important;
    }
    
    #a2as-toggle-radio label:has(input:checked) {
        box-shadow: inset 0px 4px 8px rgba(0, 0, 0, 0.2) !important;
        opacity: 1 !important;
    }

    #a2as-toggle-radio label:has(input[value="disabled"]:checked) {
        background: #6b7280 !important;
        color: white !important;
    }

    #a2as-toggle-radio label:has(input[value="enabled"]:checked) {
        background: #3b82f6 !important;
        color: white !important;
    }

    #a2as-toggle-radio label:has(input:not(:checked)) {
        background: #f3f4f6 !important;
        color: #9ca3af !important;
        opacity: 0.6 !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    """

    with gr.Blocks(title="A2AS demo", theme=gr.themes.Soft(), css=custom_css) as demo:
        gr.Markdown("# A2AS demo")
        gr.Markdown("LLM-agent behaviour demonstration when processing malicious emails")

        # A2AS Protection State
        a2as_enabled = gr.State(False)

        with gr.Row():
            # Left Column: User Emails
            with gr.Column(scale=1):
                gr.Markdown("## 📬 Your mailbox")
                gr.Markdown(f"**Email:** `{user_addr}`")

                gr.Markdown("### Received emails")
                received_display = gr.Markdown(
                    value=get_received_emails(user_addr, email_registry),
                    elem_classes="email-list",
                    max_height="400px"
                )

                gr.Markdown("### Sent emails")
                sent_display = gr.Markdown(
                    value=get_sent_emails(user_addr, email_registry),
                    elem_classes="email-list-sent",
                    max_height="400px"
                )

                refresh_btn = gr.Button("🔄 Refresh emails", variant="secondary")

            # Middle Column: Agent Chat
            with gr.Column(scale=1, elem_id="agent-column"):
                gr.Markdown("## 🤖 LLM Agent")

                # Custom Toggle Switch using Radio
                a2as_toggle = gr.Radio(
                    choices=[
                        ("a2as disabled", "disabled"),
                        ("🛡️ a2as enabled", "enabled")
                    ],
                    value="disabled",
                    show_label=False,
                    elem_id="a2as-toggle-radio",
                    container=False
                )

                gr.Markdown("Agent has access to the tools `find_emails` and `send_email` in user's mailbox")

                # Agent column wrapper for styling
                with gr.Column(elem_id="agent-wrapper"):
                    chatbot = gr.Chatbot(
                        height=500,
                        label="Chat with agent",
                        show_label=True
                    )

                    msg = gr.Textbox(
                        label="Your message",
                        placeholder="Example: 'Find all emails about token' or 'Send email to the example@mail.com' with subject ... and body ...",
                        lines=2
                    )

                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear chat")

            # Right Column: Attacker Interface
            with gr.Column(scale=1):
                gr.Markdown("## 🎭 Hacker's mailbox")
                gr.Markdown(f"**Email:** `{attacker_addr}`")
                gr.Markdown("Here you can send malicious emails to a user to test the llm agent")

                attacker_subject = gr.Textbox(
                    label="Subject",
                    placeholder="Enter email's subject",
                    lines=1
                )

                attacker_body = gr.Textbox(
                    label="Body",
                    placeholder="Enter email's body",
                    lines=8
                )

                attacker_send_btn = gr.Button("📤 Send email to user", variant="primary")

                attacker_status = gr.Markdown("")

                gr.Markdown("### Hacker's sent emails")
                attacker_sent_display = gr.Markdown(
                    value=get_sent_emails(attacker_addr, email_registry),
                    elem_classes="email-list",
                    max_height="400px"
                )

                gr.Markdown("### Hacker's received emails")
                attacker_received_display = gr.Markdown(
                    value=get_received_emails(attacker_addr, email_registry),
                    elem_classes="email-list",
                    max_height="400px"
                )

        # Event handlers
        def toggle_a2as_state(toggle_value):
            """Toggle A2AS protection state"""
            is_enabled = (toggle_value == "enabled")
            return is_enabled

        def user_submit(message, history):
            history = history or []
            history.append({"role": "user", "content": message})
            return "", history

        def bot_respond(history, a2as_enabled_state):
            if not history or history[-1]["role"] != "user":
                return history, get_received_emails(user_addr, email_registry), get_sent_emails(user_addr,
                                                                                                email_registry), get_received_emails(
                    attacker_addr, email_registry)

            user_message = history[-1]["content"][0]["text"]

            # Pass A2AS state to chat function
            bot_response = chat_with_agent_fn(user_message, a2as_enabled=a2as_enabled_state)

            # Add protection notice if A2AS blocked something
            # if a2as_enabled_state and "injection" in bot_response.lower():
            #     bot_response = "🛡️ **A2AS Protection Alert**: Potential prompt injection detected and blocked.\n\n" + bot_response

            history.append({"role": "assistant", "content": bot_response})

            return history, get_received_emails(user_addr, email_registry), get_sent_emails(user_addr,
                                                                                            email_registry), get_received_emails(
                attacker_addr, email_registry)

        # Toggle A2AS state and apply visual changes
        a2as_toggle.change(
            toggle_a2as_state,
            [a2as_toggle],
            [a2as_enabled],
            js="""
            (toggle_value) => {
                const agentWrapper = document.getElementById('agent-wrapper');
                if (agentWrapper) {
                    if (toggle_value === 'enabled') {
                        agentWrapper.classList.add('protected-mode');
                    } else {
                        agentWrapper.classList.remove('protected-mode');
                    }
                }
                return toggle_value;
            }
            """
        )

        # Chat interactions
        msg.submit(
            user_submit,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_respond,
            [chatbot, a2as_enabled],
            [chatbot, received_display, sent_display, attacker_received_display]
        )

        submit_btn.click(
            user_submit,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_respond,
            [chatbot, a2as_enabled],
            [chatbot, received_display, sent_display, attacker_received_display]
        )

        clear_btn.click(lambda: reset_agent_fn(), None, chatbot)

        # Attacker email sending
        attacker_send_btn.click(
            lambda subject, body: send_email(attacker_addr, user_addr, subject, body, email_registry),
            [attacker_subject, attacker_body],
            [attacker_status, received_display, attacker_sent_display]
        )

        # Refresh button
        refresh_btn.click(
            lambda: refresh_emails(user_addr, attacker_addr, email_registry),
            None,
            [received_display, sent_display, attacker_sent_display, attacker_received_display]
        )

        demo.load(
            lambda: refresh_emails(user_addr, attacker_addr, email_registry),
            None,
            [received_display, sent_display, attacker_sent_display, attacker_received_display]
        )

    return demo