from get_all_tickers.get_tickers import get_tickers
import yfinance as yf
import pandas as pd
from loguru import logger


# tickers = get_tickers(NYSE=False, NASDAQ=True, AMEX=False)  # We need only NASDAQ
tickers = ["GOOGL"]


def get_all_data() -> pd.DataFrame:
    # TODO: settings for interval?;
    logger.debug("Data update started")
    data = yf.download(tickers, interval='1m', period="5d")
    logger.success("Data updated finished!")
    return data


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    return df["Open"]


def save_data(df: pd.DataFrame) -> None:
    df.to_pickle("tickers.pkl")
    logger.success("Data successfully saved")
    # TODO: add DB support


if __name__ == '__main__':
    logger.info("Starting update")
    save_data(process_data(get_all_data()))
