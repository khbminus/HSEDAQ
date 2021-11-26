import time

from db.types import Tournament  # TODO: move types from db?
from db.tournaments import get_all_tournaments, save_tournament, get_tournament_participants, get_tournament
from db.users import get_user, save_user
from datetime import datetime
from view.tournaments import send_finish_statistics, send_start_message


# TODO: options?
def create_tournament(start_time: datetime, end_time: datetime) -> Tournament:
    tournaments = get_all_tournaments()
    if len(tournaments) == 0:
        next_id = 0
    else:
        next_id = max(tournaments, key=lambda x: x.tournament_id).tournament_id + 1  # TODO: query db?
    tour = Tournament(tournament_id=next_id, start_time=start_time, end_time=end_time)
    save_tournament(tour)
    return tour


def complete_pending_tournaments() -> None:
    time_now = datetime.now()  # TODO: replace with db query?
    pending = list(filter(lambda t: t.end_time <= time_now and not t.is_ended, get_all_tournaments()))
    for tournament in pending:
        send_finish_statistics(tournament, get_tournament_participants(tournament))


def start_tournaments() -> None:
    time_now = datetime.now()
    pending = list(filter(lambda t: t.start_time >= time_now and not t.is_started, get_all_tournaments()))
    for tournament in pending:
        send_start_message(tournament)


def check_correct_code_phrase(code_phrase: str) -> bool:
    return code_phrase.isdigit() and get_tournament(int(code_phrase)) is not None


def enter_tournament(user_id: int, code_phrase: str) -> None:
    tournament = get_tournament(int(code_phrase))  # If code phrase is not id
    user = get_user(user_id)
    if user is None or tournament is None:
        raise ValueError  # Replace with custom exception
    user.tournament_id, user.money = tournament.tournament_id, 1000  # starting parameters
    save_user(user)


def tournaments_polling() -> None:
    while True:
        complete_pending_tournaments()
        time.sleep(30)  # TODO: Add as parameter?


def create_code_phrase(tournament: Tournament) -> str:
    """
    Generate code phrase to enter tournament for /enter <tournament> instead of using deep linking
    :param tournament: tournament to link with
    :return: code phrase
    """
    return str(tournament.tournament_id)  # WOW
