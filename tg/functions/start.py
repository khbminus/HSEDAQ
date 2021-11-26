from tg.bot import Bot
from telebot.types import Message
from db.types import User
from db.users import get_user, save_user
from loguru import logger

bot = Bot().bot


@bot.message_handler(commands=['start'])
def start_command(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    if user is None:
        logger.info(f"User {message.from_user.username} isn't have record in the database.")
        user = User(
            user_id=uid,
            chat_id=cid,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name)
        save_user(user)

    bot.send_message(chat_id=cid, text=f"Welcome, {user.first_name}. Use `/help` for list of commands.")
