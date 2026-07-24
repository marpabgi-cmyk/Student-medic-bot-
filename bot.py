import os
import threading
from flask import Flask
import telebot
from openai import OpenAI

# 1. Ініціалізація Flask для сервісу Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Student Medic Bot is Running!"

# 2. Основна логіка Telegram-бота
def run_bot():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not telegram_token or not openai_api_key:
        print("ПОМИЛКА: Перевірте змінні оточення (TELEGRAM_TOKEN або OPENAI_API_KEY не знайдені)!")
        return

    bot = telebot.TeleBot(telegram_token)
    client = OpenAI(api_key=openai_api_key)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        try:
            # Запит до OpenAI GPT-4o-mini
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ти — професійний медичний асистент 'Студент-Медик'. Відповідай чітко, структуровано та українською мовою."},
                    {"role": "user", "content": message.text}
                ]
            )
            bot_reply = response.choices[0].message.content
            bot.reply_to(message, bot_reply)
        except Exception as e:
            print(f"Error handling message: {e}")
            bot.reply_to(message, "Вибачте, виникла помилка при обробці вашого запиту.")

    print("Telegram bot started polling...")
    bot.infinity_polling()

# 3. Запуск у двох потоках

        
