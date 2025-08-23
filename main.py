import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")  # Render'да қўшилади
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! 🎬 Kino bot ishga tushdi!")

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.reply_to(message, f"Siz yozdingiz: {message.text}")

bot.polling()
