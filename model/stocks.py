from typing import Optional
from db.stocks import get_symbols, get_price, add_long, Long, get_long, Short, add_short, get_short, \
    get_overdue_shorts, get_shorts_portfolio
from db.users import save_user, User, get_user
from db.tournaments import get_tournament
from datetime import datetime, timedelta
from tg.tournaments import send_overdue_message, get_float
from loguru import logger
from decimal import Decimal


def basic_checks(symbol: Optional[str], amount: int, user: User) -> Optional[str]:
    if symbol is not None and symbol not in get_symbols():
        return "Unknown symbol"

    if user.tournament_id is None:
        return "You don't participate in tournament"

    if amount <= 0:
        return f"Amount -- positive integer, but {amount} isn't"

    tournament = get_tournament(user.tournament_id)

    if not tournament.is_started:
        return "Please wait for the start of the tournament"


def buy_stock(symbol: str, amount: int, user: User) -> Optional[str]:  # FIXME: replace with custom Exceptions
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    tournament = get_tournament(user.tournament_id)
    price = get_price(symbol)
    current_price = price * amount

    if current_price > user.money:
        return f"Not enough money: {amount} of {symbol} costs ${get_float(current_price)}, " \
               f"but you have only ${get_float(user.money)}"

    user.money -= current_price
    save_user(user)
    add_long(Long(user_id=user.user_id, tournament_id=tournament.tournament_id, amount=amount, symbol=symbol))


def sell_stock(symbol: str, amount: int, user: User) -> Optional[str]:  # FIXME: replace with custom Exceptions
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    tournament = get_tournament(user.tournament_id)
    price = get_price(symbol)
    current_price = price * amount
    long = get_long(user.user_id, tournament.tournament_id, symbol)
    if long.amount < amount:
        return f"Can't sell {amount} of {symbol} because you have only {long.amount}"

    user.money += current_price
    save_user(user)
    long.amount = -amount
    add_long(long)


def short_stock(symbol: str, amount: int, user: User) -> Optional[str]:
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    shorts = get_shorts_portfolio(user.user_id, user.tournament_id)
    current_shorts = Decimal(0)
    for short in shorts:
        current_shorts += get_price(short.symbol) * short.amount

    price = get_price(symbol)
    current_price = price * amount
    if current_shorts + current_price >= 100000:
        return "Too many shorts. You can't short more than $100,000"

    user.money += current_price
    save_user(user)
    add_short(Short(user_id=user.user_id, tournament_id=user.tournament_id, symbol=symbol, amount=amount,
                    buy_date=datetime.now()))


def return_short(symbol: str, amount: int, user: User) -> Optional[str]:
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    tournament = get_tournament(user.tournament_id)
    price = get_price(symbol)
    current_price = price * amount
    short = get_short(user.user_id, tournament.tournament_id, symbol)
    if short.amount < amount:
        return f"Can't return {amount} of {symbol} because you ought only {short.amount}"
    if current_price > user.money:
        return f"Can't return {amount} of {symbol} because it costs {get_float(current_price)}, " \
               f"however you have just {get_float(user.money)}"

    user.money -= current_price
    save_user(user)
    short.amount = -amount
    add_short(short)


def return_short_by_index(index: int, amount: int, user: User) -> Optional[str]:
    if (err := basic_checks(None, amount, user)) is not None:
        return err
    short = get_shorts_portfolio(user.user_id, user.tournament_id)[index]
    price = get_price(short.symbol)
    current_price = price * amount
    if short.amount < amount:
        return f"Can't return {amount} of {short.symbol} because you ought only {short.amount}"
    if current_price > user.money:
        return f"Can't return {amount} of {short.symbol} because it costs {get_float(current_price)}, " \
               f"however you have just {get_float(user.money)}"

    user.money -= current_price
    save_user(user)
    short.amount = -amount
    add_short(short)


def overdue_shorts():
    now = datetime.now() - timedelta(days=1)
    for short in get_overdue_shorts(now):
        user = get_user(short.user_id)
        price = get_price(short.symbol)
        current_price = price * short.amount
        user.money -= current_price
        save_user(user)
        send_overdue_message(user, short, current_price)
        short.amount *= -1
        add_short(short)
