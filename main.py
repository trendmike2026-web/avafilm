import telebot
import json
import os

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728

bot = telebot.TeleBot(TOKEN)
DB_FILE = "movies.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Салом! Бу бот орқали сиз янги фильмлар ва сериалларни кўришингиз мумкин.\n\n🔢 Менга кино рақамини ёзинг ва мен сизга топиб бераман.")

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

@bot.message_handler(func=lambda m: True)
def send_movie(message):
    movies = load_movies()
    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")

print("✅ Bot ишга тушди...")
bot.infinity_polling()
