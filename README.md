# 🤖 Telegram AI Бот с поддержкой tool calling

Бот для Telegram с поддержкой OpenAI-совместимых моделей (через API) и инструментов (`tool_call`). Позволяет отправлять письма, сохранять и искать контакты, а также автоматически отвечать на сообщения.

## 🚀 Быстрый старт

1. Создайте файл `.env` на основе `.env.example` и заполните переменные:

   ```env
   TELEGRAM_TOKEN=...
   TELEGRAM_MAIN_CHAT_ID=...
   OPENAI_API_BASE=...
   OPENAI_API_KEY=...
   OPENAI_API_MODEL=/qwen3
   ```

2. Запустите бота:

   ```bash
   docker compose up -d
   ```

3. Напишите боту в Telegram.

---

## 🧰 Поддерживаемые функции (tool calls)

Бот умеет вызывать следующие функции:

### 📧 `send_email`

Отправить письмо по email.

```json
{
  "to_email": "user@example.com",
  "subject": "Тема письма",
  "body": "Текст письма"
}
```

---

### 💬 `send_message`

Ответить пользователю текстовым сообщением.

```json
{
  "text": "Привет! Как могу помочь?"
}
```

---

### 📇 `add_contact`

Сохранить контакт.

```json
{
  "name": "Алексей",
  "phone": "+79991234567",
  "email": "alex@example.com"
}
```

---

### 📋 `list_contacts`

Показать все сохранённые контакты.

```json
{}
```

---

### 🔍 `resolve_contact`

Найти email по имени контакта.

```json
{
  "name": "Алексей",
  "user_id": 412940515
}
```

---

## 📝 Заметки

* История сообщений сохраняется в PostgreSQL.
* Для отправки писем используется внешняя функция `send_email` из `mail.py`.
* Tool calling поддерживается только при правильной конфигурации модели (см. `tool_choice` и `tools`).
