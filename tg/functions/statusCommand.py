from tg.bot import Bot
from telebot.types import Message
from db.users import get_user
from db.tournaments import get_tournament
from db.stocks import get_longs_portfolio, get_shorts_portfolio, get_price
from datetime import timedelta

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
               f"{(short.buy_date + timedelta(days=1)).strftime('%l:%M%p on %b %d, %Y')}"
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
                                           f"Your money: ${user.money:.2f}\n"
                                           f"Portfolio:\n{get_portfolio(uid, tournament.tournament_id)}")
