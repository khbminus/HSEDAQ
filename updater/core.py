from get_all_tickers.get_tickers import get_tickers
import yfinance as yf
import pandas as pd
from loguru import logger
from db import stocks


# tickers = get_tickers(NYSE=False, NASDAQ=True, AMEX=False)  # We need only NASDAQ
tickers = ["GOOGL", "EBAY"]


def get_all_data() -> pd.DataFrame:
    # TODO: settings for interval?;
    logger.debug("Data update started")
    data = yf.download(tickers, interval='1m', period="5d", group_by="ticker")
    logger.success("Data updated finished!")
    return data


if __name__ == '__main__':
    logger.info("Starting update")
    stocks.update_stocks(get_all_data())
