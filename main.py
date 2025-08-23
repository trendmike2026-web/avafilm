import telebot
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 786536728
bot = telebot.TeleBot(TOKEN)

DB_FILE = "movies.json"

# JSONни ўқиш
def load_movies():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# JSONга ёзиш
def save_movies(movies):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

movies = load_movies()

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Салом! Кино рақамини ёзинг ва бот сизга юбориб беради.")

# Админ кино қўшиши
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Бу функция фақат админ учун!")

    movie_id = str(len(movies) + 1)  # Автоматик рақам
    movies[movie_id] = {"file_id": message.video.file_id, "title": ""}
    save_movies(movies)

    bot.reply_to(message, f"✅ Кино сақланди! Рақами: {movie_id}")

# Рақам + ном билан қўшиш (фақат админ)
@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Бу функция фақат админ учун!")

    try:
        _, movie_id, *title = message.text.split(" ")
        title = " ".join(title) if title else ""
        movies[movie_id] = {"file_id": None, "title": title}
        save_movies(movies)
        bot.reply_to(message, f"✅ {movie_id}-рақамли кино қўшилди. {title}")
    except:
        bot.reply_to(message, "❌ Фойдаланиш: /add <рақам> [ном]")

# Фойдаланувчилар рақам юборганда
@bot.message_handler(func=lambda m: m.text.isdigit())
def send_movie(message):
    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        if movie["file_id"]:
            bot.send_video(message.chat.id, movie["file_id"], caption=movie.get("title", ""))
        else:
            bot.reply_to(message, f"🎬 {movie.get('title','Кино')} (файл йўқ)")
    else:
        bot.reply_to(message, "❌ Бу рақамли кино топилмади.")

print("🤖 Bot is running...")
bot.infinity_polling()
