import telebot
import json
import os

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728  # сизинг Telegram ID

bot = telebot.TeleBot(TOKEN)

# JSON файл
DB_FILE = "movies.json"

# Агар файл йўқ бўлса яратамиз
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

# JSON ўқиш
def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# JSON сақлаш
def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# /start буйруғи
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 Салом! Бу бот орқали сиз янги фильмлар ва сериалларни кўришингиз мумкин.\n\n"
        "🔢 Менга кино рақамини ёзинг ва мен сизга топиб бераман."
    )

# Видео қабул қилиш (фақат админ)
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return  # оддий фойдаланувчилар юклай олмайди

    movies = load_movies()
    movie_id = str(len(movies) + 1)  # автоматик рақам

    caption = message.caption if message.caption else ""
    file_id = message.video.file_id

    movies[movie_id] = {"file_id": file_id, "title": caption}
    save_movies(movies)

    bot.reply_to(message, f"✅ Кино сақланди! Рақами: {movie_id}")

# Фойдаланувчи рақам юборганда
@bot.message_handler(func=lambda m: True)
def send_movie(message):
    movies = load_movies()
    movie_id = message.text.strip()

    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], c_]()_
