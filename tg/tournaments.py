from db.types import Tournament, User, Short
from typing import List
from tg.bot import Bot
from typing import Optional
from db.tournaments import get_tournament_by_code
from db.stocks import get_longs_portfolio, get_prices
from decimal import Decimal
from tg.keyboards import tournament_menu, main_menu
from db.users import save_user
from tg.utils import get_float

bot = Bot().bot


def send_finish_statistics(tournament: Tournament, users: List[User]) -> None:
    for user in users:
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.last_message_id, text="Processing...",
                              reply_markup=None)
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.last_message_id,
                              text=f"Tournament has ended!\nResults: {get_statistics(tournament, users)}",
                              reply_markup=None)

        last_message = bot.send_message(chat_id=user.chat_id, text="Choose action:", reply_markup=main_menu())
        user.last_message_id = last_message.message_id
        save_user(user)


def send_start_message(tournament: Tournament, users: List[User]) -> None:
    for user in users:
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.last_message_id,
                              text="Tournament has started!\n Choose action:", reply_markup=tournament_menu())


def check_new_tournament(code: str) -> Optional[str]:
    tournament = get_tournament_by_code(code)
    if tournament is None:
        return "Tournament doesn't exists"
    if tournament.is_ended:
        return "Tournament has ended"


def send_overdue_message(user: User, short: Short, price: Decimal):
    bot.send_message(chat_id=user.chat_id,
                     text=f"You have the late payment: {short.amount} of {short.symbol} bought in "
                          f"{short.buy_date.strftime('%l:%M%p on %b %d, %Y')}. You have paid ${get_float(price)}")


def get_statistics(tournament: Tournament, users: List[User]) -> str:
    prices = get_prices()
    ordered_user = sorted([(sum([long.amount * prices[long.symbol]
                                 for long in
                                 get_longs_portfolio(user.user_id, tournament.tournament_id)]) + user.money,
                            user) for user in users], reverse=True)
    result = ''
    for index, pair in enumerate(ordered_user, start=1):
        value, user = pair
        result += f'{index}. {user.first_name} {user.last_name} with ${get_float(value)} worth of stocks\n'
    return result
