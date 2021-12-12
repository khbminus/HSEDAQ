from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from model.tournaments import create_tournament
from loguru import logger
from typing import Optional, List
from datetime import datetime
from db.users import get_user, save_user

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
    # if start_time - now < timedelta(seconds=30):
    #     return "Can't create tournament that starts in less than 30 seconds"


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
                     text=f"Successfully created new tournament with code phrase {tournament.code}\n"
                          f"Use `/enter {tournament.code}` to enter to the tournament\n"
                          f"Once the tournament starts, you will not be able to leave it until"
                          "the end of the tournament."
                          f"Also, new users may use https://t.me/hsedaq\\_devbot?start={tournament.code} to start.")


@bot.callback_query_handler(func=lambda c: c.data == 'new')
def callback_create_tournament(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    user = get_user(cid)
    user.sketch_query = "create_a"
    user.sketch_text = None
    save_user(user)
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Please specify start date "
                                                                           "(format: `dd.mm.yyyy hh:mm:ss`): ",
                          reply_markup=None)
    # Waiting to start time
