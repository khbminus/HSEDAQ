from db.types import Stock
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row
from pandas import DataFrame
import datetime


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


def get_stock(symbol: str) -> Stock:
    date_now = datetime.datetime.now()
    logger.debug(f"Getting stock {symbol} at {date_now}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Stock)) as cur:
            res = cur.execute("SELECT * from stocks "
                              "where fetch_date = (SELECT max(fetch_date) "
                              "from stocks where ticker = %s and fetch_date < %s) "
                              "and ticker=%s;", (symbol, date_now, symbol)).fetchone()
    return res
