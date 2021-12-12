from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from model.tournaments import enter_tournament, check_correct_code_phrase
from loguru import logger
from typing import Optional, List
from db.users import get_user, save_user
from db.tournaments import get_tournament
from tg.tournaments import check_new_tournament
from tg.keyboards import tournament_menu, back_to_main

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
                         f" Entering tournament {arguments[0]}")
        return True
    if tournament.tournament_id == -1:
        return True  # default tournament, can exit
    bot.send_message(cid, f"You are currently in active tournament! Sorry :(")
    return False


@bot.message_handler(commands=['enter'])
def command_enter_tournament(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_enter(arguments)
    if not check_another_tournament(uid, cid, arguments):
        logger.debug(f"User {uid} tried to enter tournament while being at tournament")
        return
    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    new_tournament_error = check_new_tournament(arguments[0])
    if new_tournament_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad tournament id: {new_tournament_error}")
        return

    if (err := enter_tournament(uid, arguments[0])) is not None:
        logger.error(f"Validate failed with query {message.text}!")
        bot.send_message(chat_id=cid, text=f"WTF?! I'm failed:( Try again later\nError: {err}",
                         reply_markup=back_to_main())
    else:
        bot.send_message(chat_id=cid,
                         text="You have entered to the tournament. " +
                              "Choose action:", reply_markup=tournament_menu())


@bot.callback_query_handler(func=lambda c: c.data == 'enter')
def callback_enter_tournament(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Please enter a code phrase: ",
                          reply_markup=None)

    user = get_user(cid)
    user.sketch_query = "enter"
    user.sketch_text = None
    save_user(user)
    # Waiting to code phrase
