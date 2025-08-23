import telebot

# Siz bergan token
TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
bot = telebot.TeleBot(TOKEN)

# Kanal ID'lari
CHANNELS = [-1001206627592, -1002486463697, -1002909479609]

# Obuna tekshiruvchi funksiya
def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# /start buyrug'i
@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        bot.reply_to(message, "🎬 Салом! Ботдан фойдаланишингиз мумкин ✅\nМenga кино рақамини ёзинг.")
    else:
        text = "❌ Ботдан фойдаланиш учун қуйидаги каналларга обуна бўлинг:\n\n"
        text += "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
        text += "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
        text += "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
        text += "✅ Обуна бўлганингиздан сўнг /start ни қайта босинг!"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

bot.infinity_polling()
