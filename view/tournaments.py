from db.types import Tournament, User
from typing import List


# TODO: need one more table for property
# TODO: this must be in Bot class

def send_finish_statistics(tournament: Tournament, users: List[User]) -> None:
    pass


def create_code_phrase(tournament: Tournament) -> str:
    """
    Generate code phrase to enter tournament for /enter <tournament> instead of using deep linking
    :param tournament: tournament to link with
    :return: code phrase
    """
    return str(tournament.tournament_id)  # WOW
