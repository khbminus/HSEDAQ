from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from db.users import get_user, save_user
from db.stocks import get_shorts_portfolio
from db.tournaments import get_tournament
from model.tournaments import enter_tournament, create_tournament
from model.stocks import buy_stock, short_stock, sell_stock, return_short_by_index
from tg.keyboards import back_to_main, tournament_menu, back_to_tournament, main_menu, leave_tournament
from loguru import logger
from datetime import datetime

bot = Bot().bot


def check_handler(message: Message):
    logger.debug(f"{message.content_type}, {message.text}")
    return message.content_type == 'text' and not message.text.startswith('/')


@bot.message_handler(func=check_handler)
def state_handler(message: Message):
    cid = message.chat.id
    uid = message.from_user.id
    user = get_user(uid)
    text = message.text
    logger.debug(f"User {uid} sent text: {text}. Sketch Query: {user.sketch_query}")

    last_message = None
    if user.sketch_query is None:
        return

    if user.sketch_query == 'enter':
        if (err := enter_tournament(uid, text)) is not None:
            last_message = bot.send_message(chat_id=cid, text=err, reply_markup=back_to_main())
        else:
            user = get_user(uid)
            tournament = get_tournament(user.tournament_id)
            if tournament.is_started:
                last_message = bot.send_message(chat_id=cid, text="Tournament has started!\nChoose action:",
                                                reply_markup=tournament_menu())
            else:
                response = f"Tournament is not started\nExcepted start time: " \
                           f"{tournament.start_time.strftime('%l:%M%p on %b %d, %Y')}."
                last_message = bot.send_message(chat_id=cid, text=response, reply_markup=leave_tournament())
    elif user.sketch_query == 'buy':
        if not text.isdigit():
            last_message = bot.send_message(chat_id=cid, text="Invalid amount of stock",
                                            reply_markup=back_to_tournament())
        elif (err := buy_stock(user.sketch_text, int(text), user)) is not None:
            last_message = bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            last_message = bot.send_message(chat_id=cid,
                                            text=f"successfully bought {text} of {user.sketch_text}!",
                                            reply_markup=back_to_tournament())
    elif user.sketch_query == 'short':
        if not text.isdigit():
            last_message = bot.send_message(chat_id=cid, text="Invalid amount of stock",
                                            reply_markup=back_to_tournament())
        elif (err := short_stock(user.sketch_text, int(text), user)) is not None:
            last_message = bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            last_message = bot.send_message(chat_id=cid,
                                            text=f"successfully shorted {text} of {user.sketch_text}!",
                                            reply_markup=back_to_tournament())
    elif user.sketch_query == 'sell':
        if not text.isdigit():
            last_message = bot.send_message(chat_id=cid, text="Invalid amount of stock",
                                            reply_markup=back_to_tournament())
        elif (err := sell_stock(user.sketch_text, int(text), user)) is not None:
            last_message = bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            last_message = bot.send_message(chat_id=cid,
                                            text=f"successfully sold {text} of {user.sketch_text}!",
                                            reply_markup=back_to_tournament())
    elif user.sketch_query == 'return':
        if not text.isdigit():
            last_message = bot.send_message(chat_id=cid, text="Invalid amount of stock",
                                            reply_markup=back_to_tournament())
        else:
            symbol = get_shorts_portfolio(user.user_id, user.tournament_id)[int(user.sketch_text)].symbol
            if (err := return_short_by_index(int(user.sketch_text), int(text), user)) is not None:
                last_message = bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
            else:
                last_message = bot.send_message(chat_id=cid,
                                                text=f"successfully returned {text} of "
                                                     f"{symbol}!",
                                                reply_markup=back_to_tournament())
        user = get_user(uid)
    changed_sketch = False
    if user.sketch_query == 'create_a':  # if instead of elif is correct here
        if check_time(text):
            last_message = bot.send_message(chat_id=cid, text="Okay, specify a end date (in same format):")
            user.sketch_query = "create_b"
            user.sketch_text = text
            changed_sketch = True
        else:
            last_message = bot.send_message(chat_id=cid, text="Bad time format:(", reply_markup=back_to_main())
    elif user.sketch_query == 'create_b':
        if check_time(text):
            start_time = datetime.strptime(user.sketch_text, "%d.%m.%Y %H:%M:%S")
            end_time = datetime.strptime(text, "%d.%m.%Y %H:%M:%S")
            tournament = create_tournament(start_time, end_time)
            bot.send_message(chat_id=cid,
                             text=f"Successfully created new tournament with code phrase {tournament.code}\n"
                                  f"Use enter button to enter to the tournament\n"
                                  f"Once the tournament starts, you will not be able to leave it until"
                                  "the end of the tournament."
                                  f"Also, new users may use "
                                  f"https://t.me/hsedaq\\_bot?start={tournament.code} to start.")
            last_message = bot.send_message(chat_id=cid,
                                            text="Choose action:", reply_markup=main_menu())

    user.last_message_id = last_message.message_id
    if not changed_sketch:
        user.sketch_query = None
        user.sketch_text = None
    save_user(user)


def check_time(text: str) -> bool:
    # noinspection PyBroadException
    try:
        datetime.strptime(text, "%d.%m.%Y %H:%M:%S")
        return True
    except Exception:
        return False
