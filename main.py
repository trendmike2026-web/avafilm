import telebot

TOKEN = "SIZNING_BOT_TOKENINGIZ"
bot = telebot.TeleBot(TOKEN)

CHANNELS = [-1001206627592, -1002486463697, -1002909479609]

def check_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Xato: {e}")
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_subscriptions(user_id):
        text = (
            "🎬🎬🎬🎬🎬🎬🎬🎬🎬\n\n"
            "👋 *Салом!* 🎥\n\n"
            "✅ Бу бот орқали кино рақамини киритсангиз,\n"
            "сизга фильм чиқиб келади.\n\n"
            "👇 Қуйида кино рақамини юборинг 👇\n\n"
            "🎬🎬🎬🎬🎬🎬🎬🎬🎬"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        text = (
            "🚫🚫🚫🚫🚫🚫🚫🚫🚫\n\n"
            "❌ *Ботдан фойдаланиш учун аввал каналларга обуна бўлинг!*\n\n"
            "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
            "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
            "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
            "✅ Обуна бўлганингиздан сўнг /start ни қайта босинг!\n\n"
            "🚫🚫🚫🚫🚫🚫🚫🚫🚫"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_movie_number(message):
    user_id = message.from_user.id
    if check_subscriptions(user_id):
        movie_number = message.text
        response = (
            f"🎥 *Сиз киритган рақам:* {movie_number}\n\n"
            "(Бу ерга фильмни юбориш кодини қўшиш керак)"
        )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        text = (
            "🚫🚫🚫🚫🚫🚫🚫🚫🚫\n\n"
            "❌ *Ботдан фойдаланиш учун аввал каналларга обуна бўлинг!*\n\n"
            "1️⃣ [Kanal 1](https://t.me/avafilmss)\n"
            "2️⃣ [Kanal 2](https://t.me/mysportuz)\n"
            "3️⃣ [Kanal 3](https://t.me/shoubiznes_new)\n\n"
            "✅ Обуна бўлганингиздан сўнг /start ни қайта босинг!\n\n"
            "🚫🚫🚫🚫🚫🚫🚫🚫🚫"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

print("✅ Bot ishlayapti...")
bot.infinity_polling()
