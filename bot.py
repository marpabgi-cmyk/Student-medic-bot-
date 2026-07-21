import os
from flask import Flask, request
import telebot
from openai import OpenAI

# Ініціалізація токенів з екологічних змінних
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


app = Flask(__name__)

# Головний медичний промпт для ШІ
SYSTEM_PROMPT = (
    "Ти — професійний медичний AI-асистент, який консультує українською мовою. "
    "Твоє завдання — надавати чіткі, науково обґрунтовані та зрозумілі відповіді на медичні питання, "
    "допомагати розбиратися в термінах та базових алгоритмах. "
    "Обов'язково наприкінці важливих порад нагадуй, що твої консультації мають інформаційний характер "
    "і не замінюють очного візиту до лікаря."
)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я твій цілодобовий медичний AI-асистент. Чим можу допомогти?")

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
        bot.reply_to(message, f"Виникла помилка при обробці запиту. Спробуйте пізніше.")

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # Цей URL ми оновимо після деплою на Render
    # bot.set_webhook(url='https://your-render-app.onrender.com/' + TELEGRAM_TOKEN)
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

