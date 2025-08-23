import telebot
import json
import os

TOKEN = "SIZNING_TOKENINGIZNI_KUYING"
bot = telebot.TeleBot(TOKEN)

# JSON файл номи
DB_FILE = "movies.json"

# Агар JSON йўқ бўлса, янгидан яратамиз
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# START буйруғи
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "🎬 Салом!\n"
        "Бу бот орқали сиз янги фильмлар ва сериалларни кўришингиз мумкин.\n\n"
        "📌 Менга кино рақамини ёзинг."
    )
    bot.send_message(message.chat.id, text)

# Фақат рақам қабул қилади
@bot.message_handler(func=lambda msg: msg.text.isdigit())
def send_movie(message):
    movies = load_movies()
    movie_id = message.text

    if movie_id in movies:
        bot.send_message(message.chat.id, f"📽 Мана киноконтент:\n{movies[movie_id]}")
    else:
        bot.send_message(message.chat.id, "❌ Бундай рақамли кино топилмади.")

# Фақат админ кино қўшиши мумкин
ADMIN_ID = 123456789  # ўз Telegram ID’ingизни қўйинг

@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return  # бошқаларга чиқмайди

    try:
        parts = message.text.split(" ", 2)
        movie_id = parts[1]
        movie_link = parts[2]

        movies = load_movies()
        movies[movie_id] = movie_link
        save_movies(movies)

        bot.send_message(message.chat.id, f"✅ Кино қўшилди!\nID: {movie_id}")
    except:
        bot.send_message(message.chat.id, "❌ Фойдаланиш: /add 1 https://kino-link")

bot.infinity_polling()
