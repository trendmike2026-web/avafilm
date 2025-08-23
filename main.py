import telebot

# 🔑 Бот токени
TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)

# 👤 Админ ID
ADMIN_ID = 786536728

# 📂 Кинолар (рақам → {file_id, name})
movies = {}
counter = 1

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Салом 👋\nБу бот орқали сиз янги фильмлар ва сериалларни кўришингиз мумкин.\n\nМенга кино рақамини ёзинг 🎬"
    )

# 🎥 Админ кино қўшиши
@bot.message_handler(content_types=['video'])
def handle_video(message):
    global counter
    if message.from_user.id == ADMIN_ID:
        file_id = message.video.file_id
        movies[counter] = {"file_id": file_id, "name": None}
        bot.reply_to(
            message,
            f"✅ Кино рақам {counter} сақланди!\nℹ️ Агар истасангиз, кино номини юборинг (ихтиёрий)."
        )
        bot.register_next_step_handler(message, save_name, counter)
        counter += 1

# 📝 Кино номини сақлаш (ихтиёрий)
def save_name(message, movie_id):
    if message.from_user.id == ADMIN_ID:
        if message.text.startswith("/"):  # Агар команда ёзса ном сақламаймиз
            return
        movies[movie_id]["name"] = message.text
        bot.reply_to(message, f"🎬 Кино номи сақланди: {message.text}")

# 🔢 Рақам ёки ном билан кино излаш
@bot.message_handler(func=lambda m: True)
def get_movie(message):
    text = message.text.strip()
    # Агар рақам бўлса
    if text.isdigit():
        num = int(text)
        if num in movies:
            bot.send_video(
                message.chat.id,
                movies[num]["file_id"],
                caption=movies[num]["name"] or f"Кино рақами {num}"
            )
        else:
            bot.reply_to(message, "❌ Бундай рақамли кино топилмади.")
    else:
        # Агар ном бўлса
        found = None
        for mid, data in movies.items():
            if data["name"] and text.lower() in data["name"].lower():
                found = data
                break
        if found:
            bot.send_video(message.chat.id, found["file_id"], caption=found["name"])
        else:
            bot.reply_to(message, "❌ Бундай номли кино топилмади.")

# 🔄 Ботни ишга тушириш
bot.polling(none_sto_
