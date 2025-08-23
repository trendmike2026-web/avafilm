import telebot

# 🔑 Бот токенини шу ерга қўйинг
TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)

# 👤 Фақат сиз (админ) кино қўшишингиз мумкин
ADMIN_ID = 786536728  

# Кинолар базаси (рақам -> файл_id)
movies = {}
movie_counter = 1

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Салом! Кино рақамини ёзинг ва бот сизга юбориб беради.")

# Админ кино қўшиши
@bot.message_handler(content_types=['video'])
def handle_video(message):
    global movie_counter
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Бу функция фақат админ учун!")

    # Файлни сақлаймиз
    file_id = message.video.file_id
    movies[movie_counter] = file_id

    bot.reply_to(message, f"✅ Кино сақланди!\nРақами: {movie_counter}")
    movie_counter += 1

# Фойдаланувчи рақам юборса → кино қайта юборилади
@bot.message_handler(func=lambda m: m.text.isdigit())
def send_movie(message):
    movie_id = int(message.text)
    if movie_id in movies:
        bot.send_video(message.chat.id, movies[movie_id])
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади.")

# Ботни ишга тушириш
print("🤖 Бот ишлаяпти...")
bot.infinity_polling()
