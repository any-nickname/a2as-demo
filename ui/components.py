from models.email_agent_tools import EmailRegistry
from ui.formatters import format_emails_list
from functools import partial
import gradio as gr


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
    with gr.Blocks(title="A2AS demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# A2AS demo")
        gr.Markdown("LLM-agent behaviour demonstration when processing malicious emails")
        
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
            with gr.Column(scale=1):
                gr.Markdown("## 🤖 LLM Agent")
                gr.Markdown("Agent has access to the tools `find_emails` and `send_email` in user's mailbox")
                
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
        def user_submit(message, history):
            history = history or []
            history.append({"role": "user", "content": message})
            return "", history
        
        def bot_respond(history):
            if not history or history[-1]["role"] != "user":
                return history, get_received_emails(user_addr, email_registry), get_sent_emails(user_addr, email_registry), get_received_emails(attacker_addr, email_registry)
            
            user_message = history[-1]["content"][0]["text"]
            bot_response = chat_with_agent_fn(user_message)
            history.append({"role": "assistant", "content": bot_response})
            
            return history, get_received_emails(user_addr, email_registry), get_sent_emails(user_addr, email_registry), get_received_emails(attacker_addr, email_registry)
        
        # Chat interactions
        msg.submit(
            user_submit, 
            [msg, chatbot], 
            [msg, chatbot]
        ).then(
            bot_respond,
            [chatbot],
            [chatbot, received_display, sent_display, attacker_received_display]
        )
        
        submit_btn.click(
            user_submit,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_respond,
            [chatbot],
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