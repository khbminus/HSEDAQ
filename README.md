# HSEDAQ

University project on Python: an exchange simulator as a telegram bot.

Uses real market from Yahoo finances (`yfinance`), so you can collect a portfolio from top-50 S&P 500 companies!

## Usage

Deployed telegram bot available at  [@hsedaq_bot](https://t.me/hsedaq_bot)

Bot is working on Yandex.Cloud VDS, with CD pipeline (GitHub Actions)

Stock prices are updating with `yfinance`, but have <=5 minutes delay.

## Navigation

Bot navigation are done with inline buttons or commands (probably deprecated).

Old users should run `/start` command to make the menu appear.

## Features

- Custom tournaments.
- Default tournament (updates every week)
- Shorts
- Rating
- Overall plot after tournament! (doesn't work in default tournament)

## Deployment

If you want to deployment follow these steps:

1. Install dependencies: `pip install -r requirements.txt`
2. Set `TG_BOT=<your bot token>` and `LOGURU_LEVEL=INFO` (if you don't want debug output) environment variable
3. Add project root to `PYTHONPATH` variable
4. run `tg/main.py`