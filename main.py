import os
from threading import Thread
from flask import Flask
import telebot
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_FOOTBALL_KEY")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
app = Flask(__name__)
API_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}

def api_get(endpoint, params):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", headers=HEADERS, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get("response", [])
        return []
    except:
        return []

def get_team_id(name):
    data = api_get("teams", {"search": name})
    if data:
        return data[0]["team"]["id"], data[0]["team"]["name"], None
    return None, name, None

def get_last_form(team_id):
    data = api_get("fixtures", {"team": team_id, "last": 5})
    if not data:
        return "Forme inconnue", 0
    wins = draws = losses = 0
    form_str = ""
    for f in data:
        home = f["teams"]["home"]["id"] == team_id
        gf = f["goals"]["home"] if home else f["goals"]["away"]
        ga = f["goals"]["away"] if home else f["goals"]["home"]
        if gf is None or ga is None:
            continue
        if gf > ga:
            wins += 1
            form_str += "✅"
        elif gf == ga:
            draws += 1
            form_str += "➖"
        else:
            losses += 1
            form_str += "❌"
    return f"{form_str} ({wins}V-{draws}N-{losses}D)", wins*3+draws

def get_injuries(team_id):
    data = api_get("injuries", {"team": team_id})
    return len(data)

def get_h2h(id1, id2):
    data = api_get("fixtures/headtohead", {"h2h": f"{id1}-{id2}", "last": 5})
    if not data:
        return "Pas de H2H recent"
    txt = ""
    for f in data[:3]:
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]
        gh = f["goals"]["home"]
        ga = f["goals"]["away"]
        txt += f"• {home} {gh}-{ga} {away}\n"
    return txt

@app.route('/')
def home():
    return "EMK Bot PRO V2 is Running!"

@bot.message_handler(commands=['start', 'aide', 'help'])
def start(message):
    bot.reply_to(message, "🔥 EMK Bot PRO V2 🤖\n\nJe suis ton analyste foot 24h/24!\n\n📋 Commandes:\n/prono Real Madrid vs Barcelona\n/prono PSG vs Arsenal")

@bot.message_handler(commands=['prono'])
def prono(message):
    try:
        text = message.text.replace('/prono', '').strip()
        if 'vs' not in text.lower():
            bot.reply_to(message, "❌ Format: /prono Real Madrid vs Barcelona")
            return
        parts = text.lower().split('vs')
        team_a_raw = parts[0].strip()
        team_b_raw = parts[1].strip()
        bot.reply_to(message, f"🔍 Analyse PRO V2...\n⚽ {team_a_raw} vs {team_b_raw}\n⏳ API-Football...")
        id_a, name_a, _ = get_team_id(team_a_raw)
        id_b, name_b, _ = get_team_id(team_b_raw)
        if not id_a or not id_b:
            bot.reply_to(message, f"❌ Equipe non trouvee: {team_a_raw} ou {team_b_raw}")
            return
        form_a, pts_a = get_last_form(id_a)
        form_b, pts_b = get_last_form(id_b)
        inj_a = get_injuries(id_a)
        inj_b = get_injuries(id_b)
        h2h = get_h2h(id_a, id_b)
        if pts_a > pts_b + 3:
            prono_1x2 = f"Victoire {name_a} ou Nul (1X)"
            score = "2-1"
            confiance = 75
        elif pts_b > pts_a + 3:
            prono_1x2 = f"Victoire {name_b} ou Nul (X2)"
            score = "1-2"
            confiance = 75
        else:
            prono_1x2 = "Match serre - Double chance 1X ou BTTS"
            score = "1-1"
            confiance = 68
        msg = f"🏆 ANALYSE PRO V2\n\n⚔️ {name_a} vs {name_b}\n\n📊 FORME (5 derniers):\n{name_a}: {form_a} - {inj_a} blesses\n{name_b}: {form_b} - {inj_b} blesses\n\n🤝 FACE A FACE:\n{h2h}\n🎯 PRONO:\n• {prono_1x2}\n• Score: {score}\n• Confiance: {confiance}%\n\n🤖 EMK Bot PRO V2 - ...{API_KEY[-4:]}"
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur V2: {e}")

def run_bot():
    if bot:
        bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
