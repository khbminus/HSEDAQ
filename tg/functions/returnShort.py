from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from loguru import logger
from typing import Optional, List
from model.stocks import return_short
from db.users import get_user, save_user
from tg.tournaments import get_float
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from tg.keyboards import get_shorts_keyboard

bot = Bot().bot


def validate_return(arguments: List[str]) -> Optional[str]:
    if len(arguments) < 2:
        return "Too few arguments"
    if len(arguments) > 2:
        return "Too many arguments"
    if not arguments[1].isdigit():
        return "Amount is not a number"


@bot.message_handler(commands=['return'])
def command_return_short(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    arguments = message.text.split()[1:]

    validate_error = validate_return(arguments)

    if validate_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{validate_error}' error")
        bot.send_message(chat_id=cid, text=f"Bad format: {validate_error}")
        return

    return_error = return_short(arguments[0], int(arguments[1]), get_user(uid))
    if return_error is not None:
        logger.debug(f"User {uid} tried to execute {message.text}, but this got '{return_error}' error")
        bot.send_message(chat_id=cid, text=f"Error: {return_error}")
        return
    bot.send_message(chat_id=cid, text=f"Successfully returned {arguments[1]} stocks of {arguments[0]}. "
                                       f"Your balance is ${get_float(get_user(uid).money)}")


return_short_factory = CallbackData('symbol', 'index', prefix='return')


class ReturnShortCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


bot.add_custom_filter(ReturnShortCallbackFilter())


@bot.callback_query_handler(func=lambda c: c.data == 'return')
def callback_return(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id
    user = get_user(cid)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Choose a short to return:",
                          reply_markup=get_shorts_keyboard(cid, user.tournament_id, 0, return_short_factory))


@bot.callback_query_handler(func=None, config=return_short_factory.filter())
def callback_return_short(call: CallbackQuery) -> None:
    callback_data = return_short_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=f"You are going to return {callback_data['symbol']}."
                               f" Please enter amount of stocks to return:")

    user = get_user(cid)
    user.sketch_text = callback_data['index']
    user.sketch_query = "return"
    save_user(user)
    # wait for amount
