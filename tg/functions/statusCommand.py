from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from db.users import get_user
from db.tournaments import get_tournament
from db.stocks import get_longs_portfolio, get_shorts_portfolio, get_price
from datetime import timedelta
from tg.tournaments import get_float
from tg.keyboards import back_to_tournament

bot = Bot().bot


def get_portfolio(uid: int, tid: int) -> str:
    res = '  Longs:\n'
    longs = get_longs_portfolio(uid, tid)
    for long in longs:
        price = get_price(long.symbol)
        res += f'    - `{long.symbol}`: {long.amount} x ${price:.2f} = ${long.amount * price:.2f}\n'
    res += '  Shorts:\n'
    shorts = get_shorts_portfolio(uid, tid)
    for short in shorts:
        res += f"    - {short.amount} of `{short.symbol}` until " \
               f"{(short.buy_date + timedelta(days=1)).strftime('%l:%M%p on %b %d, %Y')}\n"
    return res


@bot.message_handler(commands=['status'])
def command_status(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    if user.tournament_id is None or (tournament := get_tournament(user.tournament_id)) is None:
        bot.send_message(chat_id=cid, text="You are currently doesn't participate in tournament")
    else:
        status = ''
        if not tournament.is_started:
            status = "Not started"
        elif not tournament.is_ended:
            status = "Running"

        bot.send_message(chat_id=cid, text=f"Status: {status}\n"
                                           f"Your money: ${get_float(user.money)}\n"
                                           f"Portfolio:\n{get_portfolio(uid, tournament.tournament_id)}",
                         reply_markup=back_to_tournament())


@bot.callback_query_handler(func=lambda c: c.data == 'status')
def callback_status(call: CallbackQuery):
    message = call.message
    cid = message.chat.id

    user = get_user(cid)
    tournament = get_tournament(user.tournament_id)

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=
    f"Your money: ${get_float(user.money)}\n"
    f"Portfolio:\n{get_portfolio(cid, tournament.tournament_id)}",
                          reply_markup=back_to_tournament())
