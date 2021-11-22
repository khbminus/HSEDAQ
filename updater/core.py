import yfinance as yf
import pandas as pd
from loguru import logger
from db import stocks
from typing import List

SNP_LINK = "https://dailypik.com/top-50-companies-sp-500/"


def get_tickers_snp500() -> List[str]:
    tickers = pd.read_html(SNP_LINK)[0]
    return list(tickers['Symbol'])


def get_all_data(tickers: List[str]) -> pd.DataFrame:
    # TODO: settings for interval?;
    logger.debug("Data update started")
    data = yf.download(tickers, interval='1m', period="5d", group_by="ticker")
    logger.success("Data updated finished!")
    return data


if __name__ == '__main__':
    logger.info("Starting update")
    stocks.update_stocks(get_all_data(get_tickers_snp500()))
