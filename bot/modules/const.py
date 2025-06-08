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
            "description": "Отправить письмо по email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_email": {"type": "string", "description": "Email адрес получателя"},
                    "subject": {"type": "string", "description": "Тема письма"},
                    "body": {"type": "string", "description": "Текст письма"}
                },
                "required": ["to_email", "subject", "body"]
            }
        }
    }
]

