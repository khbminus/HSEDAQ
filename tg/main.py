from tg.bot import Bot
from model.tournaments import tournaments_polling
import threading
import tg.functions

if __name__ == '__main__':
    bot = Bot().bot
    bot_thread = threading.Thread(target=bot.infinity_polling)
    tournaments_thread = threading.Thread(target=tournaments_polling)
    bot_thread.start()
    tournaments_thread.start()
    bot_thread.join()
    tournaments_thread.join()
