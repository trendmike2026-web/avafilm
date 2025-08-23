import telebot
import json
import os

TOKEN = os.getenv("BOT_TOKEN")  # Render'да Environment Variables орқали сақланади
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 786536728  # Сизнинг Telegram ID
DATA_FILE = "movies.json"


# JSON файлни юклаш
def load_movies():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# JSON файлга ёзиш
def save_movies(movies):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=4, ensure_ascii=False)


# /start буйруғи
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Салом 👋\nБу бот орқали сиз янги фильмлар ва сериалларни кўришингиз мумкин.\n"
        "🎥 Кино қўшиш фақат админга рухсат."
    )


# Кино қўшиш (фақат админ учун)
@bot.message_handler(commands=["add"])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Бу функция фақат админ учун!")
        return
    msg = bot.reply_to(message, "Кинони рақами ва номини киритинг:\n\nМасалан: `1 The Matrix`")
    bot.register_next_step_handler(msg, save_movie_step)


def save_movie_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(" ", 1)
        movie_id = parts[0]
        movie_name = parts[1]

        movies = load_movies()
        movies[movie_id] = movie_name
        save_movies(movies)

        bot.reply_to(message, f"✅ Кино қўшилди:\n{movie_id} → {movie_name}")
    except:
        bot.reply_to(message, "❌ Формат хато! Қайта уриниб кўринг.")


# Кино олиш рақам орқали
@bot.message_handler(func=lambda m: True)
def get_movie(message):
    movies = load_movies()
    movie_id = message.text.strip()

    if movie_id in movies:
        bot.reply_to(message, f"🎬 {movies[movie_id]}")
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади.")


print("Bot ishga tushdi...")
bot.polling()
