import telebot

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)

# Каналлар ID рўйхати
CHANNELS = [-1001206627592, -1002486463697, -1002909479609]

# Обуна текшириш функцияси
def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# /start буйруғи
@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.chat.id):
        bot.send_message(
            message.chat.id,
            "🎬 Салом! Бот орқали фильм рақамини ёзинг ва керакли фильмни олинг."
        )
    else:
        text = "❌ Ботдан фойдаланиш учун қуйидаги каналларга обуна бўлинг:\n\n"
        text += "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
        text += "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
        text += "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
        text += "✅ Обуна бўлганингиздан сўнг /start ни қайта босинг!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Фильм рақамини қабул қилиш
@bot.message_handler(func=lambda m: True)
def get_film(message):
    if not check_sub(message.chat.id):
        text = "❌ Илтимос аввал каналларга обуна бўлинг:\n\n"
        text += "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
        text += "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
        text += "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
        text += "✅ Обуна бўлганингиздан сўнг /start ни қайта босинг!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return
    
    # Фильм рақами ёзилса
    bot.send_message(message.chat.id, f"🎥 Сиз киритган рақам: {message.text}\n(Бу ерга фильмни юбориш кодини қўшиш керак)")

# Ботни ишга тушириш
bot.infinity_polling()
