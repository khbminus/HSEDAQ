from db.types import Tournament, User, Short
from typing import List
from tg.bot import Bot
from typing import Optional
from db.tournaments import get_tournament
from db.stocks import get_longs_portfolio, get_prices

bot = Bot().bot


def send_finish_statistics(tournament: Tournament, users: List[User]) -> None:
    for chat in set([user.chat_id for user in users]):
        bot.send_message(chat_id=chat,
                         text=f"Tournament has ended!\nResults: {get_statistics(tournament, users)}")


def send_start_message(tournament: Tournament, users: List[User]) -> None:
    for chat in set([user.chat_id for user in users]):
        bot.send_message(chat_id=chat,
                         text="Tournament has started! Use `/buy <symbol> <amount>` to buy stocks, " +
                              "`/sell <symbol> <amount>` to sell, " +
                              "`/short <symbol> <amount>` to short stocks")


def check_new_tournament(tournament_id: int) -> Optional[str]:
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return "Tournament doesn't exists"
    if tournament.is_ended:
        return "Tournament has ended"


def send_overdue_message(user: User, short: Short, price: float):
    bot.send_message(chat_id=user.chat_id,
                     text=f"You have the late payment: {short.amount} of {short.symbol} bought in "
                          f"{short.buy_date.strftime('%l:%M%p on %b %d, %Y')}. You have paid ${price:.2f}")


def get_statistics(tournament: Tournament, users: List[User]) -> str:
    prices = get_prices()
    ordered_user = sorted([(sum([long.amount * prices[long.symbol]
                                 for long in get_longs_portfolio(user.user_id, tournament.tournament_id)]) + user.money,
                            user) for user in users], reverse=True)
    result = ''
    for index, pair in enumerate(ordered_user, start=1):
        value, user = pair
        result += f'{index}. {user.first_name} {user.last_name} with ${value:.2f} worth of stocks\n'
    return result
