import time

from db.types import Tournament  # TODO: move types from db?
from db.tournaments import get_all_tournaments, save_tournament
from datetime import datetime, timedelta


# TODO: options?
def create_tournament(start_time: datetime, duration: timedelta) -> Tournament:
    tournaments = get_all_tournaments()
    next_id = max(tournaments, key=lambda x: x.tournament_id).tournament_id
    tour = Tournament(tournament_id=next_id, start_time=start_time, end_time=start_time + duration)
    save_tournament(tour)
    return tour


def completed_pending_tournaments() -> None:
    time_now = datetime.now()  # TODO: replace with db query?
    pending = list(filter(lambda t: t.end_time <= time_now and not t.is_ended, get_all_tournaments()))
    for tournament in pending:
        # TODO: Add closing in View
        pass


def tournaments_polling() -> None:
    while True:
        time.sleep(30)  # TODO: Add as parameter?


