import telebot

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 786536728  # сиз
CHANNEL_ID = "@kanal_nomi"  # каналиңиз номи

# Каналга обуна текширувчи функция
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# /start буйруғи
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        bot.reply_to(message, "👋 Салом! Бу ерда сиз кино рақамини ёзиб, кинони олишингиз мумкин.")
    else:
        bot.reply_to(
            message,
            "❗️ Кино кўриш учун аввал каналимизга обуна бўлинг:\n👉 @kanal_nomi"
        )

# Кино рақами ёзганда
@bot.message_handler(func=lambda msg: msg.text and msg.text.isdigit())
def send_movie(message):
    if not is_subscribed(message.from_user.id):
        return bot.reply_to(
            message,
            "❗️ Илтимос, аввал каналга обуна бўлинг:\n👉 @kanal_nomi"
        )
    
    movie_id = int(message.text)
    # Кино базасидан топиш керак (ҳозирча тест учун)
    bot.reply_to(message, f"🎬 {movie_id}-рақамли кино тайёр!")

# Админ кино юбориши
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Фақат админ кино қўшиши мумкин!")
    bot.reply_to(message, "✅ Кино сақланди!")

bot.infinity_polling()
