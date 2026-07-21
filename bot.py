import os
from flask import Flask, request
import telebot
from openai import OpenAI

# Ініціалізація токенів з екологічних змінних
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Головний медичний промпт для ШІ
SYSTEM_PROMPT = (
    "Ти – професійний медичний AI-асистент, який консультує студентів-медиків та інтернів. "
    "Твоє завдання – надавати чіткі, науково обґрунтовані відповіді з медицини, "
    "допомагати розбиратися в термінах та базових алгоритмах. "
    "Обов'язково наприкінці важливих порад нагадуй, що твої відповіді мають навчальний характер "
    "і не замінюють очного візиту до лікаря."
)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я твій цілодобовий медичний AI-асистент. Задай мені будь-яке питання з медицини або навчання!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Запит до OpenAI (модель gpt-4o-mini)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        response_text = completion.choices[0].message.content
        bot.reply_to(message, response_text)
    except Exception as e:
        bot.reply_to(message, f"Виникла помилка при обробці запиту: {str(e)}")

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # Автоматично підхоплює URL вашого Render-сервісу
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        bot.set_webhook(url=render_url + '/' + TELEGRAM_TOKEN)
        return f"Webhook set to {render_url}", 200
    return "Bot is running (no RENDER_EXTERNAL_URL set)", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    
