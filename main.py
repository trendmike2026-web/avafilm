import telebot
import json
from flask import Flask, request

# 🔑 Бот токени
TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 🎬 Кино базаси
def load_movies():
    with open("movies.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ▶️ /start буйруғи
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎬 Салом!\nКино рақамини юборинг (масалан: 1, 2 ...)"
    )

# 🎬 Рақам бўйича кино юбориш
@bot.message_handler(func=lambda msg: msg.text.isdigit())
def get_movie(message):
    movies = load_movies()
    movie_id = int(message.text)

    for movie in movies:
        if movie["id"] == movie_id:
            bot.send_video(
                message.chat.id,
                movie["file_id"],
                caption=f"🎥 {movie['title']}"
            )
            return
    
    bot.send_message(message.chat.id, "❌ Бундай рақамли кино йўқ.")

# 🎥 File ID олиш (фақат админ учун)
@bot.message_handler(content_types=["video"])
def save_file_id(message):
    print(message.video.file_id)  # Render логларда кўрилади
    bot.reply_to(message, f"✅ File ID: {message.video.file_id}")

# 🌐 Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# 🚀 Render'да ишга тушириш учун
@app.route("/")
def index():
    return "Bot is running!", 200
