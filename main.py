# EMK BOT V8 FINAL MONETISE - @EmkFootIA2026Bot
# Admin: 5793308081 - Emmanuel Kahiba
# Paiement: Airtel 0992200588 Mariam / Vodacom 0821220238 Emmanuel

import os
import telebot
from flask import Flask
from threading import Thread
from datetime import date
from collections import defaultdict
import random

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5793308081

PREMIUM_USERS_ENV = os.environ.get("PREMIUM_USERS", "")
VIP_USERS_ENV = os.environ.get("VIP_USERS", "")
PREMIUM_USERS = set([x.strip() for x in PREMIUM_USERS_ENV.split(",") if x.strip()])
VIP_USERS = set([x.strip() for x in VIP_USERS_ENV.split(",") if x.strip()])
PREMIUM_USERS.add(str(ADMIN_ID))
VIP_USERS.add(str(ADMIN_ID))

FREE_LIMIT = 3
usage_count = defaultdict(lambda: {"date": date.today(), "count": 0})

AIRTEL_MONEY = "0992200588 (Mariam)"
VODACOM_MONEY = "0821220238 (Emmanuel)"
CONTACT_ADMIN = "@EmkFootIA2026Bot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "EMK V8 FINAL Live", 200

def get_count(uid):
    uid = str(uid)
    if usage_count[uid]["date"] != date.today():
        usage_count[uid] = {"date": date.today(), "count": 0}
    return usage_count[uid]["count"]

def add_count(uid):
    uid = str(uid)
    if usage_count[uid]["date"] != date.today():
        usage_count[uid] = {"date": date.today(), "count": 0}
    usage_count[uid]["count"] += 1

def is_premium(uid): return str(uid) in PREMIUM_USERS or str(uid) in VIP_USERS
def is_vip(uid): return str(uid) in VIP_USERS

def calc_prono(match_text):
    random.seed(match_text.lower())
    p1 = random.randint(35,68)
    pX = random.randint(15,28)
    p2 = 100 - p1 - pX
    s1 = random.randint(0,3)
    s2 = random.randint(0,2)
    if p1 < p2: s1,s2 = s2,s1
    xG1 = round(random.uniform(0.8,2.4),1)
    xG2 = round(random.uniform(0.5,1.9),1)
    conf = max(p1,pX,p2)
    return p1,pX,p2,f"{s1}-{s2}",xG1,xG2,conf

@bot.message_handler(commands=['start','help'])
def start_h(m):
    uid = m.from_user.id
    if is_vip(uid): status="👑 VIP ILLIMITÉ ACTIF (11$/mois)"
    elif is_premium(uid): status="💎 PREMIUM ACTIF (4$/semaine)"
    else: status=f"🆓 FREE: {FREE_LIMIT - get_count(uid)}/3 essais aujourd'hui"
    bot.reply_to(m,
        f"⚽️ *EMK FOOT IA 2026 - ELOFOOT GOLD V8*\n\n{status}\n\n👉 `/prono PSG vs Arsenal`\n\n"
        f"🆓 *FREE (0$):* 3 pronos/jour, juste 1X2\n\n"
        f"💎 *PREMIUM 4$/semaine:*\n✅ Score exact + xG\n✅ Pronos illimités\n\n"
        f"👑 *VIP 11$/mois:*\n✅ Tout Premium + Combi du jour\n\n"
        f"📱 *PAYER:*\nAirtel Money: {AIRTEL_MONEY}\nVodacom M-Pesa: {VODACOM_MONEY}\n\n"
        f"Envoie preuve + /myid à {CONTACT_ADMIN}",
        parse_mode="Markdown")

@bot.message_handler(commands=['myid'])
def myid_h(m):
    bot.reply_to(m, f"Ton ID: `{m.from_user.id}`\nEnvoie-le avec la preuve de paiement.", parse_mode="Markdown")

@bot.message_handler(commands=['activate'])
def activate_h(m):
    if m.from_user.id != ADMIN_ID:
        bot.reply_to(m, "⛔️ Admin seulement."); return
    try:
        parts = m.text.split()
        new_id = parts[1]
        level = parts[2].lower() if len(parts)>2 else "premium"
        if level=="vip":
            VIP_USERS.add(new_id)
            bot.reply_to(m, f"✅ {new_id} activé 👑 VIP.\nAjoute-le dans Render > VIP_USERS pour garder après redémarrage.")
        else:
            PREMIUM_USERS.add(new_id)
            bot.reply_to(m, f"✅ {new_id} activé 💎 PREMIUM.\nAjoute-le dans Render > PREMIUM_USERS pour garder après redémarrage.")
    except:
        bot.reply_to(m, "Usage:\n/activate ID premium\n/activate ID vip")

@bot.message_handler(commands=['prono'])
def prono_h(m):
    uid = m.from_user.id
    txt = m.text.replace("/prono","").strip()
    if not txt or "vs" not in txt.lower():
        bot.reply_to(m, "Tape: `/prono Real vs Barca`", parse_mode="Markdown"); return
    if not is_premium(uid):
        if get_count(uid) >= FREE_LIMIT:
            bot.reply_to(m,
                f"🔒 *LIMITE FREE ATTEINTE (3/jour)*\n\n"
                f"💎 PREMIUM 4$/semaine\n👑 VIP 11$/mois\n\n"
                f"📱 Paiement:\nAirtel: {AIRTEL_MONEY}\nVodacom: {VODACOM_MONEY}\n\n"
                f"Envoie preuve + ID `{uid}` à {CONTACT_ADMIN}",
                parse_mode="Markdown"); return
        add_count(uid)
    p1,pX,p2,score,xG1,xG2,conf = calc_prono(txt)
    if is_premium(uid):
        bot.reply_to(m,
            f"🏆 *ELOFOOT GOLD V8 - {'VIP 👑' if is_vip(uid) else 'PREMIUM 💎'}*\n"
            f"⚔️ {txt.upper()}\n\n🎯 Score: *{score}* ({conf}%)\n📊 xG: {xG1} vs {xG2}\n"
            f"📈 1:{p1}% X:{pX}% 2:{p2}%\n🔥 Confiance: {conf}%",
            parse_mode="Markdown")
    else:
        left = FREE_LIMIT - get_count(uid)
        winner = "1 (Domicile)" if p1>p2 and p1>pX else "X (Nul)" if pX>p1 and pX>p2 else "2 (Extérieur)"
        bot.reply_to(m,
            f"⚽️ *PRONO FREE*\n⚔️ {txt.upper()}\n\n👉 Pari: *{winner}*\n\n"
            f"💎 Score exact {score} réservé Premium.\nIl te reste {left}/3 essais.",
            parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))).start()
    print(f"V8 FINAL lancé - Admin {ADMIN_ID}")
    bot.infinity_polling()
