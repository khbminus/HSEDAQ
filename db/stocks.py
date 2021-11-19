from db.types import Stock
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row
from pandas import DataFrame


def update_stocks(stocks_frame: DataFrame) -> None:
    logger.debug(f"Updating {stocks_frame.shape[0]} stocks")
    for ticker in stocks_frame.columns.levels[0]:
        processed_list = [(ticker, timestamp.to_pydatetime(), price) for timestamp, price in
                          zip(stocks_frame.index, stocks_frame[ticker]["Open"])]
        with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
            with conn.cursor(row_factory=class_row(Stock)) as cur:
                cur.executemany("""INSERT INTO stocks(ticker, fetch_date, price)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING; """, processed_list)
    logger.debug(f"Saved {stocks_frame.shape[0]} stocks")
