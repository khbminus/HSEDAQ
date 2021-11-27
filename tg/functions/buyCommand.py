from tg.bot import Bot
from telebot.types import Message
from loguru import logger
from typing import Optional, List
from model.stocks import buy_stock
from db.users import get_user

bot = Bot().bot


def validate_buy_stock(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 2:
        return "Too few arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    if not arguments[1].isdigit():
        return "Amount is not a number"


@bot.message_handler(commands=['buy'])
def command_buy_stock(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_buy_stock(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    buy_error = buy_stock(arguments[0], int(arguments[1]), get_user(uid))
    if buy_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{buy_error}' error")
        bot.send_message(chat_id=cid, text=f"Error: {buy_error}")
        return
    bot.send_message(chat_id=cid, text=f"Successfully bought {arguments[1]} stocks of {arguments[0]}. "
                                       f"Your balance is ${get_user(uid).money:.2f}")
