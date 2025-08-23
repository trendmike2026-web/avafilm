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

# === Файллар бор-йўқлигини текшириш ===
if not os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)

# === JSON функциялар ===
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

# === ADMIN PANEL ===
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Кино қўшиш", callback_data="add_movie"))
    markup.add(types.InlineKeyboardButton("📂 Рўйхат", callback_data="list_movies"))
    markup.add(types.InlineKeyboardButton("🗑 Кино ўчириш", callback_data="delete_movie"))
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    markup.add(types.InlineKeyboardButton("📢 Реклама", callback_data="post"))
    bot.send_message(message.chat.id, "⚙️ <b>Админ панел</b>", parse_mode="HTML", reply_markup=markup)

adding_movie = False
deleting_movie = False
waiting_for_post = False

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    global adding_movie, deleting_movie, waiting_for_post

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
        text = "🎬 <b>Кино рўйхати</b>\n\n"
        for movie_id, movie in movies.items():
            text += f"{movie_id}. {movie['title']}\n"
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")

    elif call.data == "delete_movie":
        deleting_movie = True
        bot.send_message(call.message.chat.id, "🗑 Қайси кино рақамини ўчирмоқчисиз? Юборинг.")

    elif call.data == "stats":
        users = load_users()
        text = (
            f"📊 <b>Статистика</b>\n\n"
            f"👥 Жами: {len(users['users'])}\n"
            f"🔎 Қидирувлар: {users['search_count']}\n"
            f"🎬 Жўнатилганлар: {users['sent_movies']}"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")

    elif call.data == "post":
        waiting_for_post = True
        bot.send_message(call.message.chat.id, "📢 Реклама хабарини юборинг (матн, фото ёки видео).")

# === VIDEO ADD ===
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

# === DELETE / SEARCH ===
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_delete_or_search(message):
    global deleting_movie
    if deleting_movie and message.from_user.id == ADMIN_ID:
        movies = load_movies()
        movie_id = message.text.strip()
        if movie_id in movies:
            del movies[movie_id]
            save_movies(movies)
            bot.reply_to(message, f"🗑 Кино {movie_id} ўчирилди!")
        else:
            bot.reply_to(message, "❌ Бундай рақам йўқ.")
        deleting_movie = False
    else:
        send_movie(message)

# === MOVIE SEARCH ===
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

# === POST ===
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video'])
def handle_post(message):
    global waiting_for_post
    if waiting_for_post and message.from_user.id == ADMIN_ID:
        users = load_users()
        sent = 0
        for user_id in users["users"]:
            try:
                if message.content_type == "text":
                    bot.send_message(user_id, message.text)
                elif message.content_type == "photo":
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
                elif message.content_type == "video":
                    bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
                sent += 1
            except:
                pass
        bot.reply_to(message, f"✅ Реклама {sent} та фойдаланувчига жўнатилди!")
        waiting_for_post = False

# === FLASK WEBHOOK ===
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
