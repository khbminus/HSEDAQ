from tg.bot import Bot
from telebot.types import Message
from model.tournaments import enter_tournament, check_correct_code_phrase
from loguru import logger
from typing import Optional, List

bot = Bot().bot


def validate_enter(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 1:
        return "Specify enter code phrase"
    if len(arguments) > 1:
        return "Too many arguments"
    if not check_correct_code_phrase(arguments[1]):
        return "Incorrect code phrase"
    return None


@bot.message_handler(commands=['enter'])
def command_create_tournament(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_enter(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return
    try:
        enter_tournament(uid, arguments[1])
    except ValueError:
        logger.error(f"Validate failed with query {message.text}!")
        bot.send_message(chat_id=cid, text=f"WTF?! I'm failed:( Try again later")
    else:
        bot.send_message(chat_id=cid,
                         text="You have entered to the tournament. " +
                              "Use `/status` to get information about the tournament.")
