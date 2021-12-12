from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from loguru import logger
from typing import Optional, List
from model.stocks import sell_stock
from db.users import get_user, save_user
from tg.tournaments import get_float
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from tg.keyboards import get_longs_keyboard

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


sell_factory = CallbackData('symbol', prefix='sell')


class SellCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


bot.add_custom_filter(SellCallbackFilter())


@bot.callback_query_handler(func=lambda c: c.data == 'sell')
def callback_sell(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id
    user = get_user(cid)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Choose a stock to sell:",
                          reply_markup=get_longs_keyboard(cid, user.tournament_id, 0, sell_factory))


@bot.callback_query_handler(func=None, config=sell_factory.filter())
def callback_sell_stock(call: CallbackQuery) -> None:
    callback_data = sell_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=f"You are going to sell {callback_data['symbol']}."
                               f" Please enter amount of stocks to sell:")

    user = get_user(cid)
    user.sketch_text = callback_data['symbol']
    user.sketch_query = "sell"
    save_user(user)
    # wait for amount
