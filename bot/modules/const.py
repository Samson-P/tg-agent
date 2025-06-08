SYSTEM_PROMPT = """
Ты помощник-бот. Если пользователь просит отправить письмо — 
обязательно верни function_call с названием 'send_email' и параметрами to_email, subject, body. 
Никаких отговорок, никаких объяснений — просто вызывай функцию. 
Для остальных запросов отвечай как обычно.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Отправляет письмо",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_email": {"type": "string", "description": "Email получателя"},
                    "subject": {"type": "string", "description": "Тема письма"},
                    "body": {"type": "string", "description": "Тело письма"}
                },
                "required": ["to_email", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Отправляет текстовое сообщение пользователю",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Ответ пользователю"}
                },
                "required": ["text"]
            }
        }
    }
]

