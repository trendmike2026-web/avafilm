import telebot
import json
import os
from telebot import types

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728

bot = telebot.TeleBot(TOKEN)

# 📂 Fayllar
MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

# Fayllarni yaratib qo'yish
if not os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)


# 🔹 JSON bilan ishlash
def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 📌 START komandasi
@bot.message_handler(commands=['start'])
def start(message):
    users = load_json(USERS_FILE)
    if message.from_user.id not in users["users"]:
        users["users"].append(message.from_user.id)
        save_json(USERS_FILE, users)

    bot.reply_to(message, "👋 Салом! Сиз ботдан фойдаланишингиз мумкин.\n\n"
                          "🔢 Кино рақамини ёзинг ва мен сизга топиб бераман.")


# 🎥 Видео сақлаш (фақат ADMIN)
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    movies = load_json(MOVIES_FILE)
    movie_id = str(len(movies) + 1)
    caption = message.caption if message.caption else ""
    movies[movie_id] = {"file_id": message.video.file_id, "title": caption}
    save_json(MOVIES_FILE, movies)
    bot.reply_to(message, f"✅ Кино сақланди! Рақами: {movie_id}")


# 🔎 Фойдаланувчи кино излайди
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def send_movie(message):
    movies = load_json(MOVIES_FILE)
    users = load_json(USERS_FILE)

    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])
        users["search_count"] += 1
        users["sent_movies"] += 1
        save_json(USERS_FILE, users)
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")


# 📊 Statistika (faqat admin)
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    text = f"📊 <b>Статистика</b>\n\n"
    text += f"👥 Жами фойдаланувчилар: {len(users['users'])}\n"
    text += f"🔎 Кино қидирганлар: {users['search_count']}\n"
    text += f"🎬 Жўнатилган кинолар: {users['sent_movies']}"
    bot.send_message(message.chat.id, text, parse_mode="HTML")


# 📢 Reklama (matn, rasm, video)
@bot.message_handler(commands=['post'])
def post(message):
    if message.from_user.id != ADMIN_ID:
        return

    users = load_json(USERS_FILE)
    if len(users["users"]) == 0:
        bot.reply_to(message, "❌ Ҳали обуначилар йўқ.")
        return

    sent = 0
    # Agar reply qilingan bo'lsa (rasm, video)
    if message.reply_to_message:
        for user_id in users["users"]:
            try:
                if message.reply_to_message.photo:
                    bot.send_photo(user_id, message.reply_to_message.photo[-1].file_id,
                                   caption=message.reply_to_message.caption or "")
                elif message.reply_to_message.video:
                    bot.send_video(user_id, message.reply_to_message.video.file_id,
                                   caption=message.reply_to_message.caption or "")
                else:
                    bot.send_message(user_id, message.reply_to_message.text)
                sent += 1
            except:
                pass
    else:
        # faqat matn yuborilsa
        text = message.text.replace("/post", "").strip()
        if not text:
            bot.reply_to(message, "❌ Реклама матни ёзинг: `/post Реклама`", parse_mode="Markdown")
            return
        for user_id in users["users"]:
            try:
                bot.send_message(user_id, f"📢 {text}")
                sent += 1
            except:
                pass

    bot.reply_to(message, f"✅ Реклама {sent} та фойдаланувчига юборилди!")


print("✅ Bot ишга тушди...")
bot.infinity_polling()
