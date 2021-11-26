from tg.bot import Bot
from telebot.types import Message
from model.tournaments import create_tournament, create_code_phrase
from loguru import logger
from typing import Optional, List
from datetime import datetime, timedelta

bot = Bot().bot


def validate_create_tournament_command(arguments: List[str], now: datetime) -> Optional[str]:
    if len(arguments) < 2:
        return "Not enough arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    for name, time in (("start time", arguments[0]), ("end time", arguments[1])):
        try:
            datetime.fromisoformat(time)
        except ValueError:
            return f"Invalid time format of {name}"
    start_time = datetime.fromisoformat(arguments[0])
    end_time = datetime.fromisoformat(arguments[1])

    if start_time >= end_time:
        return "Incorrect order of start/end time"
    if start_time - now < timedelta(seconds=30):
        return "Can't create tournament that starts in less than 30 seconds"


@bot.message_handler(commands=['create_tournament'])
def command_create_tournament(message: Message):
    now = datetime.now()
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_create_tournament_command(arguments, now)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return
    start_time = datetime.fromisoformat(arguments[0])
    end_time = datetime.fromisoformat(arguments[1])
    tournament = create_tournament(start_time, end_time)

    logger.info(f"Created new tournament {tournament}")

    bot.send_message(chat_id=cid,
                     text=f"Successfully created new tournament with code phrase {tournament.tournament_id}\n"
                          f"Use `/enter {create_code_phrase(tournament)}` to enter to the tournament")
