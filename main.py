import telebot
import json
import os
from telebot import types

TOKEN = "8427740917:AAEeRDdLZreYIoQQRezHFBINeTGC7Ed7c4M"
ADMIN_ID = 786536728   # 🔑 ўз ID’ингни қўй

# Kanal ID'лари
CHANNELS = ["-1001206627592", "-1002486463697", "-1002909479609"]

# Kanal linklari
CHANNEL_LINKS = [
    ("https://t.me/avafilmss", "Kanal 1"),
    ("https://t.me/mysportuz", "Kanal 2"),
    ("https://t.me/shoubiznes_new", "Kanal 3")
]

bot = telebot.TeleBot(TOKEN)

# Fayllar
MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"

# Агар файл йўқ бўлса, яратиб қўямиз
if not os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": [], "search_count": 0, "sent_movies": 0}, f, ensure_ascii=False, indent=4)


# --- Database functions ---
def load_movies():
    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_user(user_id):
    users = load_users()
    if user_id not in users["users"]:
        users["users"].append(user_id)
        save_users(users)


# --- Subscription check ---
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


# --- Start command ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)

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


# --- Save video (admin only) ---
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


# --- Search movie ---
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def send_movie(message):
    movies = load_movies()
    users = load_users()

    movie_id = message.text.strip()
    if movie_id in movies:
        movie = movies[movie_id]
        bot.send_video(message.chat.id, movie["file_id"], caption=movie["title"])
        users["sent_movies"] += 1
        save_users(users)
    else:
        bot.reply_to(message, "❌ Бундай рақамли кино топилмади!")


# --- Stats ---
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


# --- Post text ---
@bot.message_handler(commands=['post'])
def post(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/post", "").strip()
    if not text:
        bot.reply_to(message, "❌ Реклама матни ёзинг: `/post Реклама матни`", parse_mode="Markdown")
        return

    users = load_users()
    sent = 0
    for user_id in users["users"]:
        try:
            bot.send_message(user_id, f"📢 {text}")
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Реклама {sent} та фойдаланувчига юборилди!")


# --- Post photo ---
@bot.message_handler(commands=['post_photo'])
def post_photo(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.reply_to(message, "❌ Илтимос, /post_photo буйруғини расмга реплай қилиб ёзинг!")
        return

    caption = message.text.replace("/post_photo", "").strip()
    users = load_users()
    sent = 0
    file_id = message.reply_to_message.photo[-1].file_id
    for user_id in users["users"]:
        try:
            bot.send_photo(user_id, file_id, caption=caption)
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Расм {sent} та фойдаланувчига юборилди!")


# --- Post video ---
@bot.message_handler(commands=['post_video'])
def post_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.reply_to_message or not message.reply_to_message.video:
        bot.reply_to(message, "❌ Илтимос, /post_video буйруғини видеога реплай қилиб ёзинг!")
        return

    caption = message.text.replace("/post_video", "").strip()
    users = load_users()
    sent = 0
    file_id = message.reply_to_message.video.file_id
    for user_id in users["users"]:
        try:
            bot.send_video(user_id, file_id, caption=caption)
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Видео {sent} та фойдаланувчига юборилди!")


print("✅ Bot ишга тушди...")
bot.infinity_polling()
