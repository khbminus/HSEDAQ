from typing import Optional
from db.stocks import get_symbols, get_stock, add_long, Long, get_long, Short, add_short, get_short
from db.users import save_user, User
from db.tournaments import get_tournament
from datetime import datetime
from loguru import logger


def basic_checks(symbol: str, amount: int, user: User) -> Optional[str]:
    if symbol not in get_symbols():
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
    stock = get_stock(symbol)
    current_price = stock.price * amount

    if current_price - user.money > 1e-3:
        return f"Not enough money: {amount} of {symbol} costs ${current_price:.3f}, but you have only ${user.money:.3f}"

    user.money -= current_price
    save_user(user)
    add_long(Long(user_id=user.user_id, tournament_id=tournament.tournament_id, amount=amount, symbol=symbol))


def sell_stock(symbol: str, amount: int, user: User) -> Optional[str]:  # FIXME: replace with custom Exceptions
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    tournament = get_tournament(user.tournament_id)
    stock = get_stock(symbol)
    current_price = stock.price * amount
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

    stock = get_stock(symbol)
    current_price = stock.price * amount

    user.money += current_price
    save_user(user)
    add_short(Short(user_id=user.user_id, tournament_id=user.tournament_id, symbol=symbol, amount=amount,
                    buy_date=datetime.now()))


def return_short(symbol: str, amount: int, user: User) -> Optional[str]:
    if (err := basic_checks(symbol, amount, user)) is not None:
        return err

    tournament = get_tournament(user.tournament_id)
    stock = get_stock(symbol)
    current_price = stock.price * amount
    short = get_short(user.user_id, tournament.tournament_id, symbol)
    if short.amount < amount:
        return f"Can't return {amount} of {symbol} because you ought only {short.amount}"
    if current_price - user.money > 1e-3:
        return f"Can't return {amount} of {symbol} because it costs {current_price:.3f}, " \
               f"however you have just {user.money:.3f}"

    user.money -= current_price
    save_user(user)
    short.amount = -amount
    add_short(short)
