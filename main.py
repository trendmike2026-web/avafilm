import telebot
import json
import os
from telebot import types

TOKEN = "SIZNING_BOT_TOKENingiz"
ADMIN_ID = 786536728   # ўзингизнинг Telegram ID'ингизни ёзинг

# Kanal ID'лари
CHANNELS = ["-1001206627592", "-1002486463697", "-1002909479609"]

# Kanal linklari
CHANNEL_LINKS = [
    ("https://t.me/avafilmss", "Kanal 1"),
    ("https://t.me/mysportuz", "Kanal 2"),
    ("https://t.me/shoubiznes_new", "Kanal 3")
]

bot = telebot.TeleBot(TOKEN)

DB_FILE = "movies.json"
USERS_FILE = "users.json"

# --- JSON файллар ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)

def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Каналга обуна текшириш ---
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    if message.from_user.id not in users["users"]:
        users["users"].append(message.from_user.id)
        save_users(users)

    if not check_subscription(message.from_user.id):
        text = "❌ *Кечирасиз, ботдан фойдаланиш учун қуйидаги каналларга обуна бўлинг:*"
        markup = types.InlineKeyboardMarkup()
        for url, name in CHANNEL_LINKS:
            markup.add(types.InlineKeyboardButton(f"➕ {name} га обуна бўлиш", url=url))
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        return
    
    bot.reply_to(message, 
        "👋 Салом! ✅ Сиз каналларга обуна бўлгансиз.\n\n"
        "🔢 Кино рақамини ёзинг ва мен сизга топиб бераман."
    )

# --- Обуна қайта текшириш ---
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def recheck(call):
    if check_subscription(call.from_user.id):
        bot.edit_message_text(
            "✅ Сиз обуна бўлдингиз! Энди кино рақамини юборишингиз мумкин.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Ҳали барча каналларга обуна бўлмагансиз!", show_alert=True)

# --- Кино сақлаш (фақат админ) ---
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

# --- Кино юбориш ---
@bot.message_handler(func=lambda m: m.text and m.text.strip().isdigit())
def send_movie(message):
    movies = load_movies()
    users = load_users()

    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])

        users["search_count"] += 1
        users["sent_movies"] += 1
        save_users(users)
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")

# --- Статистика ---
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    text = f"📊 <b>Статистика</b>\n\n"
    text += f"👥 Жами фойдаланувчилар: {len(users['users'])}\n"
    text += f"🔎 Кино қидирганлар: {users['search_count']}\n"
    text += f"🎬 Жўнатилган кинолар: {users['sent_movies']}"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- Реклама (матн, фото, видео) ---
@bot.message_handler(commands=['post'])
def post(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "📢 Реклама юбориш учун хабарга жавоб беринг (матн, фото ёки видео).")

@bot.message_handler(func=lambda m: m.reply_to_message and m.reply_to_message.text and m.reply_to_message.text.startswith("/post"))
def send_post(message):
    users = load_users()
    sent = 0
    for user_id in users["users"]:
        try:
            if message.content_type == "text":
                bot.send_message(user_id, message.text)
            elif message.content_type == "photo":
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == "video":
                bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Реклама {sent} та фойдаланувчига юборилди!")

print("✅ Bot ишга тушди...")
bot.infinity_polling()
