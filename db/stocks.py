from typing import Optional, Set, List
from db.types import Stock, Long, Short
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row
from pandas import DataFrame
from datetime import datetime, timedelta


def update_stocks(stocks_frame: DataFrame) -> None:
    logger.debug(f"Updating {stocks_frame.shape[0]} stocks")

    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Stock)) as cur:
            for ticker in stocks_frame.columns.levels[0]:
                current_stocks = stocks_frame[ticker]["Open"].dropna()
                processed_list = [(ticker, timestamp.to_pydatetime(), price) for timestamp, price in
                                  zip(current_stocks.index, current_stocks)]
                cur.executemany("""INSERT INTO stocks(ticker, fetch_date, price)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING; """, processed_list)
    logger.debug(f"Saved {stocks_frame.shape[0]} stocks")


def get_stock(symbol: str) -> Optional[Stock]:
    date_now = datetime.now()
    logger.debug(f"Getting stock {symbol} at {date_now}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Stock)) as cur:
            res = cur.execute("SELECT * from stocks "
                              "where fetch_date = (SELECT max(fetch_date) "
                              "from stocks where ticker = %s and fetch_date < %s) "
                              "and ticker=%s;", (symbol, date_now, symbol)).fetchone()
    return res


def get_symbols() -> Set[str]:
    logger.debug(f"Getting all available symbols")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor() as cur:
            res = cur.execute("SELECT DISTINCT ticker from stocks").fetchall()
    return set([x[0] for x in res])


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
