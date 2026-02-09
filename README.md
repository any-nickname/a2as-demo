<img src="img/a2as-logo.png" width="1024">


Practical implementation of A2AS framework on python, using smolagents for agents and gradio for web UI.

### Contents

├── [Abstract](#abstract)<br>
├── [Project description](#project-description)<br>
├── [Project setup](#project-setup)<br>
├── [Attack performing](#attack-performing)<br>
├── [How A2AS is used here](#how-a2as-is-used-here)<br>
├── [Acknowledgements](#acknowledgements)<br>
└── [License](#license)

### Abstract

If we had to describe A2AS in a couple of sentences, we could say that it is a set of the most basic, and therefore universal principles for protecting your AI agents.

The A2AS principles themselves are expressed in the form of the acronym BASIC.

These principles do not depend on specific technologies, infrastructure, or the particular expertise of your team members, and can therefore be applied to any project. If you are interested, you can learn more about A2AS on their page: https://a2as.org/ 

However, because the A2AS principles are not tied to a specific implementation, they have a slightly vague description, which can leave developers unsure of where to start when it comes to applying A2AS in practice.

The goal of the current project is to contribute to examples of A2AS usage by showing our vision of how this framework can be applied in practice, which ultimately provides a clearer picture for developers who want to implement A2AS in their projects.

### Project description

The project is a Python application with smolagents for creating agents and gradio for creating a web UI.

When the application is launched, a web page with the following content becomes available at `http://127.0.0.1:7860`:

<img src="img/web-ui-screenshot.png" width="1024">

The application's web interface consists of three main columns.

**The first (left) column** represents your mailbox with the address `user@goodcorp.ai`, containing both sent and received corporate emails from your colleagues.

**The second column (in the middle)** represents the interaction window with the AI assistant that helps you with your email. The assistant is an LLM agent that has access to the functions of reading emails from your mailbox and sending emails on your behalf. 

Also, you can choose one of two agents — a regular one and one protected by A2AS approaches. The switch above the dialog box is responsible for selecting the agent.

Finally, below the dialog box is a window for displaying agent logs, which shows the tools called by the agent and their parameters. This window allows us to check whether the agent has performed any malicious actions.

**The third column (on the right)** represents a mailbox similar to the one in the first column, but on behalf of the hacker. Note that all emails sent by the hacker will be delivered to the user's mailbox, so there is no field for specifying the email recipient here.

### Project setup

This project supports two ways of connecting llm models: using hugging face, or using local model through LM Studio. 

Before launching the project, you need to create a `.env` file in the root of the repository and fill it with the necessary data. As an example, you can use the `.env.example` file. Fill in the file according to the model connection method you are using.

### Attack performing

It's time to attack! This project proposes an attack using a prompt injection hidden inside an email sent by a hacker to a user.

<details>
    <summary>Here is an example of the steps to reproduce the attack (tap to open)</summary>

1. **Ask agent a simple action.** 

Ask an unprotected agent if you have any upcoming meetings: “Do I have a meeting scheduled?” — the agent will gather information based on the available emails. The agent will successfully complete the request and respond to you based on the available emails.

<img src="img/simple-action-1.png">

2. **Send malicious email.** 

Next, on behalf of the hacker, send the user the email described in the `attack.txt` file in the current repository. This email contains a prompt injection and is disguised as spam.

<img src="img/malicious-mail.png">

3. **Ask agent about action again.** 

Ask the unprotected agent the question again: “Do I have a meeting scheduled?” This time, the hacker's email will be included in the agent's context because it contains the word “meeting,” and the agent will then execute the instructions in that email. The email contains instructions on how to leak your corporate token.

<img src="img/simple-action-2.png">

The agent can answer differently from time to time, either revealing that it has performed a malicious action or not.

4. **Ensure that the agent has performed the malicious action.** 
 
Please note that a new item has appeared in the user's sent mail section — this is a letter with a token sent to the hacker's address. You can also check the agent logs below the dialog box to see if it called the mail sending tool:

<img src="img/agent-execution-logs.png">

The attack was successful! Agent executed malicious instruction from the hacker's email and leaked our internal token. 

If you repeat the same algorithm with the protected agent (the switch is located above the dialog box), you will see that the agent refuses to follow the instructions in the malicious email:

<img src="img/malicious-mail-refused.png">

</details>

### How A2AS is used here

The protected agent implements all five BASIC principles:

⊹ **Behavior Certificates** are implemented through the `EmailBehaviorCertificates` class, which validates each tool call before execution. For example, sending emails is only allowed to addresses within the `@goodcorp.ai` domain, and emails containing token patterns are blocked.

⊹ **Authenticated Prompts** use HMAC-SHA256 signing to verify that user messages have not been tampered with. The signature is generated when the user submits a prompt and verified before the agent processes it.

⊹ **Security Boundaries** isolate untrusted content using XML tags. User input is wrapped in `<a2as:user>` tags, making it clear to the model that this content should be treated as data, not as instructions.

⊹ **In-Context Defenses** are security meta-instructions embedded in the agent's system prompt within the `<a2as:defense>` section. These instructions explicitly tell the model to ignore any commands found inside emails or tool outputs and to reject prompt injection attempts.

⊹ **Codified Policies** define application-specific rules in the `<a2as:policy>` section of the system prompt. These rules mirror the behavior certificates, creating defense-in-depth: even if the model tries to violate a policy, the code-level check will block the action.

### Acknowledgements

Thanks to the Vladislav Tushkanov from Kaspersky AI Research Center. The initial design of the attack demonstration was inspired by his presentation “AI Agents vs. Prompt Injections” at BrigthTALK Oct 07 2025.

## License

MIT License - Vladimir Grishchenko, 2026
