import telebot
from os import environ

bot = telebot.TeleBot(environ["TG_BOT"])


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, "Okay, it's works")


bot.infinity_polling()
