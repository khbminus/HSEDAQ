from time import sleep
from tg.bot import Bot
from model.tournaments import tournaments_polling
from model.stocks import overdue_shorts
from db.tournaments import update_default_tournament
import threading
import schedule
import tg.functions

schedule.every(10).seconds.do(tournaments_polling)
schedule.every(10).seconds.do(overdue_shorts)
schedule.every().week.do(update_default_tournament)


def polling():
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    bot = Bot().bot
    bot_thread = threading.Thread(target=bot.infinity_polling)
    tournaments_thread = threading.Thread(target=polling)
    bot_thread.start()
    tournaments_thread.start()

    bot_thread.join()
    tournaments_thread.join()
