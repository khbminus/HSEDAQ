from tg.bot import Bot
from telebot.types import Message
from model.tournaments import enter_tournament, check_correct_code_phrase
from loguru import logger
from typing import Optional, List
from db.users import get_user, save_user
from db.tournaments import get_tournament
from db.types import User

bot = Bot().bot


def validate_enter(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 1:
        return "Specify enter code phrase"
    if len(arguments) > 1:
        return "Too many arguments"
    if not check_correct_code_phrase(arguments[0]):
        return "Incorrect code phrase"


def check_another_tournament(uid: int, cid: int, arguments: List[str]) -> bool:
    user = get_user(uid)
    if user.tournament_id is None:
        return True
    tournament = get_tournament(user.tournament_id)
    if not tournament.is_started:
        bot.send_message(cid,
                         f"You are currently in tournament {tournament.tournament_id}." +
                         f" Entering tournament {arguments[1]}")
        return True
    bot.send_message(cid, f"You are currently in active tournament! Sorry :(")
    return False


def check_new_tournament(tournament_id: int) -> Optional[str]:
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return "Tournament doesn't exists"
    if tournament.is_ended:
        return "Tournament has ended"


@bot.message_handler(commands=['enter'])
def command_enter_tournament(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    if user is None:
        bot.send_message(chat_id=cid, text="Wow, you aren't in the database... Strange, I'll report this")
        logger.error(f"User {user} isn't have record in the database, but using functions")
        user = User(
            user_id=uid,
            chat_id=cid,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name)
        save_user(user)

    arguments = message.text.split()[1:]

    validate_error = validate_enter(arguments)
    if not check_another_tournament(uid, cid, arguments):
        logger.debug(f"User {uid} tried to enter tournament while being at tournament")
        return
    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    new_tournament_error = check_new_tournament(int(arguments[0]))
    if new_tournament_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad tournament id: {new_tournament_error}")

    try:
        enter_tournament(uid, arguments[0])
    except ValueError:
        logger.error(f"Validate failed with query {message.text}!")
        bot.send_message(chat_id=cid, text=f"WTF?! I'm failed:( Try again later")
    else:
        bot.send_message(chat_id=cid,
                         text="You have entered to the tournament. " +
                              "Use `/status` to get information about the tournament.")
