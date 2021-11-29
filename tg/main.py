from time import sleep
from tg.bot import Bot
from model.tournaments import tournaments_polling
from model.stocks import overdue_shorts
import threading
import tg.functions


def polling():
    while True:
        tournaments_polling()
        overdue_shorts()
        sleep(10)


if __name__ == '__main__':
    bot = Bot().bot
    bot_thread = threading.Thread(target=bot.infinity_polling)
    tournaments_thread = threading.Thread(target=polling)
    bot_thread.start()
    tournaments_thread.start()
    bot_thread.join()
    tournaments_thread.join()
