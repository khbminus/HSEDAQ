from tg.bot import Bot
from telebot.types import Message
from loguru import logger
from typing import Optional, List
from model.stocks import return_short
from db.users import get_user
from tg.tournaments import get_float

bot = Bot().bot


def validate_return(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 2:
        return "Too few arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    if not arguments[1].isdigit():
        return "Amount is not a number"


@bot.message_handler(commands=['return'])
def command_return_short(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_return(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    return_error = return_short(arguments[0], int(arguments[1]), get_user(uid))
    if return_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{return_error}' error")
        bot.send_message(chat_id=cid, text=f"Error: {return_error}")
        return
    bot.send_message(chat_id=cid, text=f"Successfully returned {arguments[1]} stocks of {arguments[0]}. "
                                       f"Your balance is ${get_float(get_user(uid).money)}")
