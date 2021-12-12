from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from loguru import logger
from typing import Optional, List
from model.stocks import short_stock
from db.users import get_user, save_user
from datetime import datetime, timedelta
from tg.tournaments import get_float
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from tg.keyboards import get_stocks_menu

bot = Bot().bot


def validate_short_stock(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 2:
        return "Too few arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    if not arguments[1].isdigit():
        return "Amount is not a number"


@bot.message_handler(commands=['short'])
def command_short_stock(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_short_stock(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    short_error = short_stock(arguments[0], int(arguments[1]), get_user(uid))
    if short_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{short_error}' error")
        bot.send_message(chat_id=cid, text=f"Error: {short_error}")
        return

    due_time = datetime.now() + timedelta(days=1)  # not fair
    bot.send_message(chat_id=cid, text=f"Successfully borrowed {arguments[1]} stocks of {arguments[0]}. "
                                       f"Your balance is ${get_float(get_user(uid).money)}. "
                                       f"Due: {due_time.strftime('%l:%M%p on %b %d, %Y')}")


short_factory = CallbackData('symbol', prefix='short')


class ShortCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


bot.add_custom_filter(ShortCallbackFilter())


@bot.callback_query_handler(func=lambda c: c.data == 'short')
def callback_short(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Choose a stock to short:",
                          reply_markup=get_stocks_menu(0, short_factory))


@bot.callback_query_handler(func=None, config=short_factory.filter())
def callback_short_stock(call: CallbackQuery) -> None:
    callback_data = short_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=f"You are going to short {callback_data['symbol']}. "
                               f"Please enter amount of stocks to short:")

    user = get_user(cid)
    user.sketch_text = callback_data['symbol']
    user.sketch_query = "short"
    save_user(user)
    # wait for amount
