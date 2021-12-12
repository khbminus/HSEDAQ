from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from db.users import get_user, save_user
from db.tournaments import get_tournament
from model.tournaments import enter_tournament
from model.stocks import buy_stock, short_stock, sell_stock, return_short_by_index
from tg.keyboards import back_to_main, tournament_menu, back_to_tournament
from loguru import logger

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

    if user.sketch_query is None:
        return

    if user.sketch_query == 'enter':
        try:
            enter_tournament(uid, text)
        except ValueError:
            bot.send_message(chat_id=cid, text="Code phrase is invalid.", reply_markup=back_to_main())
        finally:
            user = get_user(uid)
            tournament = get_tournament(user.tournament_id)
            if tournament.is_started:
                bot.send_message(chat_id=cid, text="Tournament has started!\nChoose action:",
                                 reply_markup=tournament_menu())
            else:
                pass  # FIXME
    elif user.sketch_query == 'buy':
        if not text.isdigit():
            bot.send_message(chat_id=cid, text="Invalid amount of stock", reply_markup=back_to_tournament())
        elif (err := buy_stock(user.sketch_text, int(text), user)) is not None:
            bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            bot.send_message(chat_id=cid,
                             text=f"successfully bought {text} of {user.sketch_text}!",
                             reply_markup=back_to_tournament())
    elif user.sketch_query == 'short':
        if not text.isdigit():
            bot.send_message(chat_id=cid, text="Invalid amount of stock", reply_markup=back_to_tournament())
        elif (err := short_stock(user.sketch_text, int(text), user)) is not None:
            bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            bot.send_message(chat_id=cid,
                             text=f"successfully shorted {text} of {user.sketch_text}!",
                             reply_markup=back_to_tournament())
    elif user.sketch_query == 'sell':
        if not text.isdigit():
            bot.send_message(chat_id=cid, text="Invalid amount of stock", reply_markup=back_to_tournament())
        elif (err := sell_stock(user.sketch_text, int(text), user)) is not None:
            bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            bot.send_message(chat_id=cid,
                             text=f"successfully sold {text} of {user.sketch_text}!",
                             reply_markup=back_to_tournament())
    elif user.sketch_query == 'return':
        if not text.isdigit():
            bot.send_message(chat_id=cid, text="Invalid amount of stock", reply_markup=back_to_tournament())
        elif (err := return_short_by_index(int(user.sketch_text), int(text), user)) is not None:
            bot.send_message(chat_id=cid, text=err, reply_markup=back_to_tournament())
        else:
            bot.send_message(chat_id=cid,
                             text=f"successfully returned {text} of {user.sketch_text}!",
                             reply_markup=back_to_tournament())
    user = get_user(uid)
    user.sketch_query = None
    user.sketch_text = None
    save_user(user)
