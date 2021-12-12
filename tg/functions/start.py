from tg.bot import Bot
from telebot.types import Message
from db.types import User
from db.users import get_user, save_user
from loguru import logger
from .enterTournament import command_enter_tournament
from tg.keyboards import main_menu

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
            last_name=message.from_user.last_name, )
        save_user(user)
    arguments = message.text.split()[1:]

    if len(arguments) >= 1:  # deep linking
        command_enter_tournament(message)
    else:
        last_message = bot.send_message(chat_id=cid,
                                        text=f"Welcome, {user.first_name}. Choose action:",
                                        reply_markup=main_menu())

        user.last_message_id = last_message.message_id
        save_user(user)
