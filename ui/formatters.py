def format_emails_list(emails, max_body_length=100):
    """Format emails for display"""
    if not emails:
        return "No emails"
    
    def escape_markdown(text):
        """Escape special Markdown characters and newlines"""
        if not text:
            return text
        # Заменяем переносы строк на пробелы, чтобы избежать проблем с Markdown списками
        text = text.replace('\n', ' ')
        # Экранируем специальные символы Markdown
        special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
        for char in special_chars:
            text = text.replace(char, '\\' + char)
        return text
    
    result = []
    for i, email in enumerate(emails, 1):
        body = email.get('body', '')
        
        # Экранируем все поля перед выводом
        from_addr = escape_markdown(email.get('from', 'N/A'))
        to_addr = escape_markdown(email.get('to', 'N/A'))
        subject = escape_markdown(email.get('subject', 'N/A'))
        body = escape_markdown(body)
        
        result.append(f"**[Email {i}]**<br>"
                     f"&nbsp;&nbsp;&nbsp;&nbsp;From:&nbsp;&nbsp;&nbsp;&nbsp; {from_addr}<br>"
                     f"&nbsp;&nbsp;&nbsp;&nbsp;To:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {to_addr}<br>"
                     f"&nbsp;&nbsp;&nbsp;&nbsp;Subject: {subject}<br>"
                     f"<div style='max-height: 75px; overflow: overlay;'>&nbsp;&nbsp;&nbsp;&nbsp;Body:&nbsp;&nbsp;&nbsp;&nbsp; {body}</div><br>"
                     f"{'─' * 50}")
    
    return "\n\n".join(result)