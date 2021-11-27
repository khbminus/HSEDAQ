from typing import Optional, Set, List
from db.types import Long, Short
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row
from pandas import DataFrame
from datetime import datetime, timedelta
from pandas import read_html
from yfinance import download

SNP_LINK = "https://dailypik.com/top-50-companies-sp-500/"
tickers = list(read_html(SNP_LINK)[0]["Symbol"])


def get_price(symbol: str) -> float:
    date_now = datetime.now()
    logger.debug(f"Getting stock {symbol} at {date_now.strftime('%l:%M%p on %b %d, %Y')}")
    data = download(symbol, interval='1m', period="1d", group_by="ticker")
    return data["Open"].dropna()[-1]


def get_symbols() -> Set[str]:
    return set(tickers)


def add_long(stock: Long) -> None:
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT into longs(user_id, tournament_id, symbol, amount) "
                        "VALUES (%s, %s, %s, %s)"
                        "ON CONFLICT ON CONSTRAINT longs_pk DO UPDATE SET "
                        "amount = excluded.amount + longs.amount",
                        (stock.user_id, stock.tournament_id, stock.symbol, stock.amount))


def add_short(stock: Short) -> None:
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT into shorts(user_id, tournament_id, symbol, amount, buy_date) "
                        "VALUES (%s, %s, %s, %s, %s)"
                        "ON CONFLICT ON CONSTRAINT shorts_ok DO UPDATE SET "
                        "amount = excluded.amount + shorts.amount",
                        (stock.user_id, stock.tournament_id, stock.symbol, stock.amount, stock.buy_date))


def get_overdue_shorts(time: datetime, uid: int, tid: int) -> List[Short]:
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Short)) as cur:
            res = cur.execute(
                "SELECT * FROM shorts WHERE buy_date <= %s and user_id=%s and tournament_id=%s",
                (time, uid, tid)).fetchall()
    return res


def get_longs_portfolio(uid: int, tid: int) -> List[Long]:
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Long)) as cur:
            res = cur.execute(
                "SELECT * FROM longs WHERE user_id=%s and tournament_id=%s and amount != 0",
                (uid, tid)).fetchall()
    return res


def get_long(uid: int, tid: int, symbol: str) -> Long:
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Long)) as cur:
            res = cur.execute("SELECT * FROM longs WHERE user_id=%s and tournament_id=%s and symbol=%s",
                              (uid, tid, symbol)).fetchone()
    if res is None:
        return Long(user_id=uid, tournament_id=uid, amount=0, symbol=symbol)
    return res


def get_shorts_portfolio(uid: int, tid: int) -> List[Short]:
    from_date = datetime.now() - timedelta(days=1)
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Short)) as cur:
            res = cur.execute(
                "SELECT * FROM shorts WHERE user_id=%s and tournament_id=%s and buy_date >= %s",
                (uid, tid, from_date)).fetchall()
    return res


def get_short(uid: int, tid: int, symbol: str) -> Short:
    from_date = datetime.now() - timedelta(days=1)
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Short)) as cur:
            res = cur.execute(
                "SELECT * FROM shorts WHERE user_id=%s and tournament_id=%s and symbol=%s and buy_date >= %s",
                (uid, tid, symbol, from_date)).fetchone()
    return res
