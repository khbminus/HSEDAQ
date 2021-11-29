from loguru import logger
from os import environ
import telebot


class Bot(object):
    """
    Singleton Bot object to have only one instance of bot
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info('Creating new Bot instance')
            cls._instance = super(Bot, cls).__new__(cls)
            cls.bot = telebot.TeleBot(environ["TG_BOT"], parse_mode='MARKDOWN')  # TODO: Add error handling
        return cls._instance
