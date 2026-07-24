import os
from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


Thread(target=run).start()
import os
from flask import Flask, request
import telebot
from openai import OpenAI

# Отримання змінних оточення
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY, http_client=None)


app = Flask(__name__)

# Системний промпт для медичного бота
SYSTEM_PROMPT = (
    "Ти – професійний медичний AI-асистент, який консультує студентів-медиків та інтернів. "
    "Твоє завдання – надавати чіткі, науково обґрунтовані відповіді з медицини, "
    "допомагати розбиратися в термінах та базових алгоритмах. "
    "Обов'язково наприкінці важливих порад нагадуй, що твої відповіді мають навчальний характер "
    "і не замінюють очного візиту до лікаря."
)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я твій цілодобовий медичний AI-асистент Student-Medic. Задай мені будь-яке питання з медицини або навчання!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
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

# Обробник подій від Telegram
@app.route('/' + str(TELEGRAM_TOKEN), methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Головна сторінка для перевірки сервера Render
@app.route("/")
def webhook():
    return "Student-Medic Bot is running!", 200

# Встановлюємо вебхук один раз під час запуску додатка
if RENDER_EXTERNAL_URL and TELEGRAM_TOKEN:
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
        
