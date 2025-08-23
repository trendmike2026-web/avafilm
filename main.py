import telebot
from telebot import types

TOKEN = "SIZNING_BOT_TOKENINGIZ"
bot = telebot.TeleBot(TOKEN)

CHANNELS = [
    ("https://t.me/avafilmss", "📺 Kanal 1"),
    ("https://t.me/mysportuz", "⚽ Kanal 2"),
    ("https://t.me/shoubiznes_new", "🎶 Kanal 3")
]

def check_subscriptions(user_id):
    ids = [-1001206627592, -1002486463697, -1002909479609]
    for channel_id in ids:
        try:
            chat_member = bot.get_chat_member(channel_id, user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_subscriptions(user_id):
        bot.send_message(
            message.chat.id,
            "🎬 *Салом!* Сиз ботдан фойдаланишингиз мумкин.\n\nКино рақамини юборинг:",
            parse_mode="Markdown"
        )
    else:
        # Inline кнопкалар яратамиз
        keyboard = types.InlineKeyboardMarkup()
        for link, name in CHANNELS:
            keyboard.add(types.InlineKeyboardButton(f"➕ Obuna bo‘lish ({name})", url=link))
        keyboard.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))

        text = (
            "❌ *Ботдан фойдаланиш учун қуйидаги каналларга обуна бўлинг!* ❌\n\n"
            "Обуна бўлганингиздан сўнг '✅ Tasdiqlash' тугмасини босинг 👇"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def callback_check(call):
    user_id = call.from_user.id
    if check_subscriptions(user_id):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ Рахмат! Сиз барча каналларга обуна бўлдингиз.\n\nЭнди кино рақамини юборинг 🎬",
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Ҳали ҳамма каналга обуна бўлмагансиз!", show_alert=True)

print("✅ Bot ishlayapti...")
bot.infinity_polling()
