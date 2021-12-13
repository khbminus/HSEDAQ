from typing import List
from db.types import Long, Short, Tournament, User
from db.consts import DB_NAME
import psycopg
from db.tournaments import get_tournament_participants
from db.stocks import get_longs_portfolio, get_price
from datetime import datetime
from pandas import DataFrame
import pandas.io.sql as sqlio
from decimal import Decimal


def get_snapshot_dataframe(tournament: Tournament) -> DataFrame:
    with psycopg.connect(dbname=DB_NAME) as conn:
        # There isn't any sql injection, i promise :)
        return sqlio.read_sql_query(f"""SELECT concat(first_name, ' ', last_name) as name, time, snapshots.money
                                        FROM snapshots
                                                 join users u on snapshots.user_id = u.user_id
                                        where snapshots.tournament_id = {tournament.tournament_id} order by time;""",
                                    conn)


def _get_money(user: User, tournament: Tournament) -> Decimal:
    res = user.money
    stocks = get_longs_portfolio(user.user_id, tournament.tournament_id)
    for stock in stocks:
        res += stock.amount * get_price(stock.symbol)
    return res


def update_snapshots(tournament: Tournament):
    now = datetime.now()
    users = get_tournament_participants(tournament)
    update = [(user.user_id, tournament.tournament_id, now, _get_money(user, tournament)) for user in users]
    with psycopg.connect(dbname=DB_NAME, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.executemany("insert into snapshots(user_id, tournament_id, time, money) VALUES (%s, %s, %s, %s);",
                            update)
