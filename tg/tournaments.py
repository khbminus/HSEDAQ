from db.types import Tournament, User
from typing import List
from tg.bot import Bot

bot = Bot().bot


def send_finish_statistics(tournament: Tournament, users: List[User]) -> None:
    pass



def send_start_message(tournament: Tournament, users: List[User]) -> str:
    pass
