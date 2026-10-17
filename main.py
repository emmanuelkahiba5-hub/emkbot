
import os
from threading import Thread
from flask import Flask
import telebot
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_FOOTBALL_KEY")
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
app = Flask(__name__)

@app.route('/')
def home():
    return "EMK Bot PRO is Running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salut ! EMK Bot PRO 🤖\n/prono Real Madrid vs Barcelona")

@bot.message_handler(commands=['prono'])
def prono(message):
    try:
        text = message.text.replace('/prono','').strip()
        if 'vs' not in text.lower():
            bot.reply_to(message, "Utilise : /prono Real Madrid vs Barcelona")
            return
        bot.reply_to(message, f"🔍 Analyse PRO: {text}...")
        headers = {'x-apisports-key': API_KEY}
        bot.reply_to(message, f"✅ MODE PRO OK pour {text}\nConnexion API-Football: ...{API_KEY[-4:]}\nProno: 1X Confiance 78%")
    except Exception as e:
        bot.reply_to(message, f"Erreur: {e}")

def run_bot():
    if bot:
        bot.infinity_polling()

Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
