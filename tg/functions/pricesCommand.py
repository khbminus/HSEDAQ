from tg.bot import Bot
from telebot.types import Message
from db.stocks import get_prices
from tg.tournaments import get_float

bot = Bot().bot


@bot.message_handler(commands=['prices'])
def command_prices(message: Message):
    cid = message.chat.id
    message = bot.send_message(chat_id=cid, text="Processing...")
    res = ''
    for symbol, price in get_prices().items():
        res += f'`{symbol}`: ${get_float(price)}\n'

    bot.edit_message_text(chat_id=cid, message_id=message.id, text=res)
