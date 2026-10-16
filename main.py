import os
from threading import Thread
from flask import Flask
import telebot

# Ton token sera mis dans Render, pas ici
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

app = Flask(__name__)

@app.route('/')
def home():
    return "EMK Bot is Running!"

if bot:
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, "Salut ! Je suis EMK Bot 🤖 en ligne 24h/24 !")

    @bot.message_handler(func=lambda m: True)
    def echo(message):
        bot.reply_to(message, f"Tu as dit : {message.text}")

def run_bot():
    if bot:
        print("Bot démarré...")
        bot.infinity_polling()

if __name__ == "__main__":
    # Lance le bot dans un autre thread
    Thread(target=run_bot).start()
    # Lance le site web pour Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
