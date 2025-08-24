import telebot
import json
import os
from telebot import types
from flask import Flask, request

# 🔑 Токен ва Админ ID
TOKEN = os.environ.get("8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))  # ўз ID рақамингизни қўйинг

# Канал ID ва линклар
CHANNELS = ["-1001206627592", "-1002486463697"]
CHANNEL_LINKS = [
    ("https://t.me/avafilmss", "Kanal 1"),
    ("https://t.me/mysportuz", "Kanal 2")
]

bot = telebot.TeleBot(TOKEN)

MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

# Файллар тайёрлаш
if not os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)

# JSON функциялар
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

# Канал текшириш
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# Start
@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    if message.from_user.id not in users["users"]:
        users["users"].append(message.from_user.id)
        save_users(users)

    if not check_subscription(message.from_user.id):
        text = "❌ Каналларга обуна бўлиш керак!"
        markup = types.InlineKeyboardMarkup()
        for url, name in CHANNEL_LINKS:
            markup.add(types.InlineKeyboardButton(f"➕ {name}", url=url))
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    bot.reply_to(message, "👋 Салом! Кино рақамини юборинг.")

# Callback
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def recheck(call):
    if check_subscription(call.from_user.id):
        bot.edit_message_text("✅ Энди кино рақамини юборинг.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Ҳали барча каналларга обуна эмассиз!", show_alert=True)

# Admin Panel
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Кино қўшиш", callback_data="add_movie"))
    markup.add(types.InlineKeyboardButton("📂 Рўйхат", callback_data="list_movies"))
    markup.add(types.InlineKeyboardButton("🗑 Ўчириш", callback_data="delete_movie"))
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    bot.send_message(message.chat.id, "⚙️ Админ панел", reply_markup=markup)

adding_movie = False
deleting_movie = False

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    global adding_movie, deleting_movie
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "add_movie":
        adding_movie = True
        bot.send_message(call.message.chat.id, "🎬 Кино видеосини юборинг (caption → ном).")

    elif call.data == "list_movies":
        movies = load_movies()
        if not movies:
            bot.send_message(call.message.chat.id, "📂 Базада кино йўқ!")
            return
        text = "🎬 Кино рўйхати:\n\n"
        for movie_id, movie in movies.items():
            text += f"{movie_id}. {movie['title']}\n"
        bot.send_message(call.message.chat.id, text)

    elif call.data == "delete_movie":
        deleting_movie = True
        bot.send_message(call.message.chat.id, "🗑 Ўчирмоқчи бўлган кино рақамини юборинг.")

    elif call.data == "stats":
        users = load_users()
        text = f"📊 Статистика:\n👥 Фойдаланувчилар: {len(users['users'])}\n🔎 Қидирувлар: {users['search_count']}\n🎬 Жўнатилган кино: {users['sent_movies']}"
        bot.send_message(call.message.chat.id, text)

# Video add
@bot.message_handler(content_types=['video'])
def handle_video(message):
    global adding_movie
    if message.from_user.id != ADMIN_ID or not adding_movie:
        return
    movies = load_movies()
    movie_id = str(len(movies) + 1)
    caption = message.caption if message.caption else f"Kino {movie_id}"
    movies[movie_id] = {"file_id": message.video.file_id, "title": caption}
    save_movies(movies)
    bot.reply_to(message, f"✅ Кино қўшилди! Рақами: {movie_id}")
    adding_movie = False

# Delete or search
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_delete_or_search(message):
    global deleting_movie
    if deleting_movie and message.from_user.id == ADMIN_ID:
        movies = load_movies()
        movie_id = message.text.strip()
        if movie_id in movies:
            del movies[movie_id]
            save_movies(movies)
            bot.reply_to(message, f"🗑 {movie_id}-кино ўчирилди!")
        else:
            bot.reply_to(message, "❌ Бундай рақам йўқ.")
        deleting_movie = False
    else:
        send_movie(message)

# Send movie
def send_movie(message):
    movies = load_movies()
    users = load_users()
    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])
        users["sent_movies"] += 1
        save_users(users)
    else:
        users["search_count"] += 1
        save_users(users)
        bot.reply_to(message, "❌ Бундай рақамли кино йўқ!")

# Flask
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
