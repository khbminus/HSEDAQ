from typing import Optional
from db.types import User
from db.consts import DB_NAME
import psycopg
from loguru import logger
from psycopg.rows import class_row


def get_user(user_id: int) -> Optional[User]:
    logger.debug(f"Getting user with id={user_id}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(User)) as cur:
            res = cur.execute("SELECT * from users WHERE user_id=%s", (user_id,)).fetchone()
    logger.debug(f"Got user_id={user_id}: {res}")
    return res


def save_user(user: User) -> None:
    logger.debug(f"Saving {user}")
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute("""INSERT INTO users(user_id, chat_id, first_name, last_name, tournament_id, money, 
                            sketch_query, sketch_text) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (user_id) DO UPDATE 
                              SET chat_id = excluded.chat_id,
                                  first_name = excluded.first_name, 
                                  last_name = excluded.last_name,
                                  tournament_id = excluded.tournament_id,
                                  money = excluded.money,
                                  sketch_query = excluded.sketch_query,
                                  sketch_text = excluded.sketch_text
                                ;""",
                        (user.user_id, user.chat_id, user.first_name, user.last_name, user.tournament_id, user.money,
                         user.sketch_query, user.sketch_text))
    logger.debug(f"Saved {user.user_id}")
