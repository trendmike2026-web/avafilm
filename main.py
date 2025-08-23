import telebot
import json
import os
from telebot import types

# 🔑 Token ва Admin ID
TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728  # ўзингни ID қўйсан

# 🔗 Kanal ID'лари
CHANNELS = ["-1001206627592", "-1002486463697", "-1002909479609"]

# 🔗 Kanal linklari
CHANNEL_LINKS = [
    ("https://t.me/avafilmss", "Kanal 1"),
    ("https://t.me/mysportuz", "Kanal 2"),
    ("https://t.me/shoubiznes_new", "Kanal 3")
]

bot = telebot.TeleBot(TOKEN)

# 📂 Файллар
DB_FILE = "movies.json"
USERS_FILE = "users.json"

# 🎬 movies.json тайёрлаш
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

# 👤 users.json тайёрлаш
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)

# 📥 JSON функциялар
def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 👥 Фойдаланувчи қўшиш
def add_user(user_id):
    users = load_users()
    if user_id not in users["users"]:
        users["users"].append(user_id)
        save_users(users)

# 📌 Обуна текшириш
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# 🚀 START
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)  # ✅ фойдаланувчини базага қўшиш

    if not check_subscription(message.from_user.id):
        text = "❌ *Кечирасиз, ботдан фойдаланиш учун қуйидаги каналларга обуна бўлинг:*"
        markup = types.InlineKeyboardMarkup()
        for url, name in CHANNEL_LINKS:
            markup.add(types.InlineKeyboardButton(f"➕ {name} га обуна бўлиш", url=url))
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        return
    
    bot.reply_to(message, 
        "👋 Салом! ✅ Сиз каналларга обуна бўлгансиз.\n\n"
        "🔢 Кино рақамини ёзинг ва мен сизга топиб бераман."
    )

# 🔁 Recheck
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def recheck(call):
    if check_subscription(call.from_user.id):
        bot.edit_message_text(
            "✅ Сиз обуна бўлдингиз! Энди кино рақамини юборишингиз мумкин.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Ҳали барча каналларга обуна бўлмагансиз!", show_alert=True)

# 🎬 ADMIN кино юбориши
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    movies = load_movies()
    movie_id = str(len(movies) + 1)
    caption = message.caption if message.caption else ""
    movies[movie_id] = {"file_id": message.video.file_id, "title": caption}
    save_movies(movies)
    bot.reply_to(message, f"✅ Кино сақланди! Рақами: {movie_id}")

# 🎬 Фойдаланувчи кино излаши
@bot.message_handler(func=lambda m: True)
def send_movie(message):
    add_user(message.from_user.id)  # ✅ фойдаланувчини базага қўшиш
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
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")

# 📊 Статистика
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    text = f"📊 <b>Статистика</b>\n\n"
    text += f"👥 Жами фойдаланувчилар: {len(users['users'])}\n"
    text += f"🔎 Кино қидирганлар: {users['search_count']}\n"
    text += f"🎬 Жўнатилган кинолар: {users['sent_movies']}"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# 📢 Реклама
@bot.message_handler(commands=['post'])
def post(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/post", "").strip()
    if not text:
        bot.reply_to(message, "❌ Реклама матни ёзинг: `/post Реклама матни`", parse_mode="Markdown")
        return

    users = load_users()
    sent = 0
    for user_id in users["users"]:
        try:
            bot.send_message(user_id, f"📢 {text}")
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Реклама {sent} та фойдаланувчига юборилди!")

print("✅ Bot ишга тушди...")
bot.infinity_polling()
