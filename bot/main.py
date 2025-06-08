import os
import json
import asyncio
import nest_asyncio
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from modules.mail import send_email as send_email_sync
from modules.memory import save_message, get_recent_messages, init_db
from dotenv import load_dotenv
import re
from modules.const import SYSTEM_PROMPT, TOOLS

nest_asyncio.apply()
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_MAIN_CHAT_ID = int(os.getenv("TELEGRAM_MAIN_CHAT_ID", "412940515"))
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_API_MODEL", "gpt-4o")

openai.api_base = OPENAI_API_BASE
openai.api_key = OPENAI_API_KEY


def strip_think_blocks(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


async def tool_send_email(to_email: str, subject: str, body: str) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, send_email_sync, to_email, subject, body)
    return f"Письмо отправлено на {to_email}."


async def tool_send_message(text: str) -> str:
    return text


TOOL_FUNCTIONS = {
    "send_email": tool_send_email,
    "send_message": tool_send_message
}


def detect_tool(prompt: str) -> str:
    if "отправь письмо" in prompt.lower() or "email" in prompt.lower():
        return "send_email"
    return "send_message"


import asyncio
import re

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != TELEGRAM_MAIN_CHAT_ID:
        return

    user_id = update.effective_user.id
    prompt = update.message.text.strip()

    # Обработка команды сохранения контакта
    contact_match = re.match(r"запомни контакт:\s*(.+)", prompt, re.IGNORECASE)
    if contact_match:
        contact_text = contact_match.group(1)
        # Пример парсинга: "Иван Иванов, тел 123456789, email ivan@example.com"
        name_match = re.search(r"^([^,]+)", contact_text)
        phone_match = re.search(r"тел\s*([\d+]+)", contact_text, re.IGNORECASE)
        email_match = re.search(r"email\s*([\w.@+-]+)", contact_text, re.IGNORECASE)

        name = name_match.group(1).strip() if name_match else None
        phone = phone_match.group(1).strip() if phone_match else None
        email = email_match.group(1).strip() if email_match else None

        if name:
            await save_contact(user_id, name, phone, email)
            reply = f"Контакт '{name}' сохранён."
        else:
            reply = "Не удалось распознать имя контакта. Формат: 'запомни контакт: Имя, тел 12345, email example@example.com'"
        await update.message.reply_text(reply)
        return

    # Обработка команды вывода контактов
    if prompt.lower() in ["напиши все контакты, которые запомнил", "все контакты"]:
        contacts = await get_contacts(user_id)
        if not contacts:
            await update.message.reply_text("У меня нет запомненных контактов.")
        else:
            lines = []
            for c in contacts:
                line = c[0]
                if c[1]:
                    line += f", тел: {c[1]}"
                if c[2]:
                    line += f", email: {c[2]}"
                lines.append(line)
            await update.message.reply_text("\n".join(lines))
        return

    # Сохраняем пользовательское сообщение
    await save_message(user_id, "user", prompt)

    history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *await get_recent_messages(user_id),
        {"role": "user", "content": prompt}
    ]

    tool_name = detect_tool(prompt)

    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=history,
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": tool_name}}
        )

        message = response.choices[0].message

        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"].get("arguments", "{}"))

                if func_name in TOOL_FUNCTIONS:
                    result = await TOOL_FUNCTIONS[func_name](**func_args)
                    await save_message(user_id, "function", result)
                    await update.message.reply_text(result)
                else:
                    await update.message.reply_text(f"Неизвестная функция: {func_name}")
        else:
            reply = strip_think_blocks(message.get("content", ""))
            await save_message(user_id, "assistant", reply)
            await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Ошибка AI: {e}")


async def main():
    await init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот запущен.")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())

