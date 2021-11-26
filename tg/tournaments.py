from db.types import Tournament, User
from typing import List
from tg.bot import Bot

bot = Bot().bot


def send_finish_statistics(tournament: Tournament, users: List[User]) -> None:
    for chat in set([user.chat_id for user in users]):
        bot.send_message(chat_id=chat,
                         text="Tournament has ended!")


def send_start_message(tournament: Tournament, users: List[User]) -> None:
    for chat in set([user.chat_id for user in users]):
        bot.send_message(chat_id=chat,
                         text="Tournament has started! Use `/buy <symbol> <amount>` to buy stocks, " +
                              "`/sell <symbol> <amount>` to sell, " +
                              "`/short <symbol> <amount>` to short stocks")
