from tg.bot import Bot
from tg.tournaments import get_float
from telebot.types import Message, CallbackQuery
from loguru import logger
from typing import Optional, List
from model.stocks import buy_stock
from db.users import get_user, save_user
from tg.keyboards import get_stocks_menu
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

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
                                       f"Your balance is ${get_float(get_user(uid).money)}")


buy_factory = CallbackData('symbol', prefix='buy')


class BuyCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


bot.add_custom_filter(BuyCallbackFilter())


@bot.callback_query_handler(func=lambda c: c.data == 'buy')
def callback_buy(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Choose a stock to buy:",
                          reply_markup=get_stocks_menu(0, buy_factory))


@bot.callback_query_handler(func=None, config=buy_factory.filter())
def callback_buy_stock(call: CallbackQuery) -> None:
    callback_data = buy_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=f"You are going to buy {callback_data['symbol']}. Please enter amount of stocks to buy:")

    user = get_user(cid)
    user.sketch_text = callback_data['symbol']
    user.sketch_query = "buy"
    save_user(user)
    # wait for amount
