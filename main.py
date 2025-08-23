import telebot
import json
import os

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728
CHANNELS = ["-1001206627592", "-1002486463697", "-1002909479609"]

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

def check_subscription(user_id):
    """Фойдаланувчи барча каналларга обуна бўлганлигини текширади"""
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id):
        text = "📢 Ботдан фойдаланиш учун қуйидаги каналларга ОБУНА БЎЛИНГ:\n\n"
        text += "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
        text += "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
        text += "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
        text += "✅ Обуна бўлгач, /start ни қайта босинг!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return
    
    bot.reply_to(message, 
        "👋 Салом! ✅ Сиз каналларга обуна бўлгансиз.\n\n"
        "🔢 Кино рақамини ёзинг ва мен сизга топиб бераман."
    )

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
    if not check_subscription(message.from_user.id):
        text = "📢 Илтимос, аввал қуйидаги каналларга обуна бўлинг:\n\n"
        text += "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
        text += "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
        text += "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
        text += "✅ Обуна бўлгач, /start ни қайта босинг!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return
    
    movies = load_movies()
    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")

print("✅ Bot ишга тушди...")
bot.infinity_polling()
