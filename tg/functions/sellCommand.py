from tg.bot import Bot
from telebot.types import Message
from loguru import logger
from typing import Optional, List
from model.stocks import sell_stock
from db.users import get_user
from tg.tournaments import get_float

bot = Bot().bot


def validate_sell_stock(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 2:
        return "Too few arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    if not arguments[1].isdigit():
        return "Amount is not a number"


@bot.message_handler(commands=['sell'])
def command_sell_stock(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_sell_stock(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    sell_error = sell_stock(arguments[0], int(arguments[1]), get_user(uid))
    if sell_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{sell_error}' error")
        bot.send_message(chat_id=cid, text=f"Error: {sell_error}")
        return
    bot.send_message(chat_id=cid, text=f"Successfully sold {arguments[1]} stocks of {arguments[0]}. "
                                       f"Your balance is ${get_float(get_user(uid).money)}")
