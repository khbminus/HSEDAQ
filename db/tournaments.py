from typing import Optional, List
from db.types import Tournament, User
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row


def get_tournament(tournament_id: int) -> Optional[Tournament]:
    logger.debug(f"Getting tournament with id={tournament_id}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Tournament)) as cur:
            res = cur.execute("SELECT * from tournaments WHERE tournament_id=%s", (tournament_id,)).fetchone()
    logger.debug(f"Got tournament with id {tournament_id}: {res}")
    return res


def save_tournament(tournament: Tournament) -> None:
    logger.debug(f"Saving {tournament}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Tournament)) as cur:
            cur.execute("""INSERT INTO tournaments(tournament_id, start_time, end_time, is_ended, is_started) 
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (tournament_id) DO UPDATE 
                              SET start_time = excluded.start_time, 
                                  end_time = excluded.end_time,
                                  is_ended = excluded.is_ended,
                                  is_started = excluded.is_started
                                  """,
                        (tournament.tournament_id, tournament.start_time, tournament.end_time, tournament.is_ended,
                         tournament.is_started))
    logger.debug(f"Saved {tournament.tournament_id}")


def get_all_tournaments() -> List[Tournament]:
    logger.debug("Getting all tournaments")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(Tournament)) as cur:
            res = cur.execute("SELECT * from tournaments").fetchall()
    logger.debug(f"Got {len(res)} tournaments")
    return res


def get_tournament_participants(tournament: Tournament) -> List[User]:
    logger.debug(f"Getting all participants of tournament {tournament}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(User)) as cur:
            res = cur.execute("SELECT * FROM users WHERE tournament_id=%s", (tournament.tournament_id,)).fetchall()
    return res
