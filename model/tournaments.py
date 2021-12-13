from typing import Optional

from db.types import Tournament
from db.tournaments import get_all_tournaments, save_tournament, get_tournament_participants, get_tournament_by_code, \
    get_active_tournaments
from db.snapshots import update_snapshots
from db.users import get_user, save_user
from datetime import datetime
from tg.tournaments import send_finish_statistics, send_start_message
from random import choices
from string import ascii_letters


# TODO: options?
def create_tournament(start_time: datetime, end_time: datetime) -> Tournament:
    tournaments = get_all_tournaments()
    if len(tournaments) == 0:
        next_id = 0
    else:
        next_id = max(tournaments, key=lambda x: x.tournament_id).tournament_id + 1
    tour = Tournament(tournament_id=next_id, start_time=start_time, end_time=end_time, code=create_code_phrase())
    save_tournament(tour)
    return tour


def complete_pending_tournaments() -> None:
    time_now = datetime.now()
    pending = list(filter(lambda t: t.end_time <= time_now and not t.is_ended, get_all_tournaments()))
    for tournament in pending:
        send_finish_statistics(tournament, get_tournament_participants(tournament))
        tournament.is_ended = True
        for user in get_tournament_participants(tournament):
            user.tournament_id = -1
            save_user(user)
        save_tournament(tournament)


def start_tournaments() -> None:
    time_now = datetime.now()
    pending = list(filter(lambda t: t.start_time <= time_now and not t.is_started, get_all_tournaments()))
    for tournament in pending:
        send_start_message(tournament, get_tournament_participants(tournament))
        tournament.is_started = True
        save_tournament(tournament)


def check_correct_code_phrase(code_phrase: str) -> bool:
    return True  # FIXME


def enter_tournament(user_id: int, code_phrase: str) -> Optional[str]:
    tournament = get_tournament_by_code(code_phrase)  # If code phrase is not id
    user = get_user(user_id)
    if tournament is None:
        return f"Tournament with code phrase '{code_phrase}' not found"
    if tournament.is_ended:
        return f"Tournament has ended"
    user.tournament_id, user.money = tournament.tournament_id, 1000  # starting parameters
    save_user(user)


def make_snapshots():
    tournaments = get_active_tournaments()
    for tournament in tournaments:
        update_snapshots(tournament)


def tournaments_polling() -> None:
    complete_pending_tournaments()
    start_tournaments()


def create_code_phrase() -> str:
    """
    Generate code phrase to enter tournament for /enter <tournament> / deep-linking
    :return: code phrase
    """
    return ''.join(choices(ascii_letters, k=16))
