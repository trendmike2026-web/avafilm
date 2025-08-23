import telebot
import json
import os
from telebot import types
from flask import Flask, request

# 🔑 Токен ва Админ ID
TOKEN = os.environ.get("8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "786536728"))

# Канал ID'лари
CHANNELS = ["-1001206627592", "-1002486463697", "-1002909479609"]
CHANNEL_LINKS = [
    ("https://t.me/avafilmss", "Kanal 1"),
    ("https://t.me/mysportuz", "Kanal 2"),
    ("https://t.me/shoubiznes_new", "Kanal 3")
]

bot = telebot.TeleBot(TOKEN)

MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

if not os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)

# === JSON ===
def load_movies():
    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# === Канал текшириш ===
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    if message.from_user.id not in users["users"]:
        users["users"].append(message.from_user.id)
        save_users(users)

    if not check_subscription(message.from_user.id):
        text = "❌ *Кечирасиз, каналларга обуна бўлиш керак!*"
        markup = types.InlineKeyboardMarkup()
        for url, name in CHANNEL_LINKS:
            markup.add(types.InlineKeyboardButton(f"➕ {name}", url=url))
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        return

    bot.reply_to(message, "👋 Салом! 🔢 Кино рақамини юборинг.")

# === Callback: обунани қайта текшириш ===
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def recheck(call):
    if check_subscription(call.from_user.id):
        bot.edit_message_text(
            "✅ Сиз обуна бўлдингиз! Энди кино рақамини юборинг.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Ҳали барча каналларга обуна эмассиз!", show_alert=True)

# === Flask Webhook ===
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
