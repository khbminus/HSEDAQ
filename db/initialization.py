import psycopg
from loguru import logger


# TODO: add config for db

def create_wrapper(db_name: str, command: str, table_name: str) -> None:
    try:
        with psycopg.connect(dbname=db_name, autocommit=True) as conn:
            with conn.cursor() as cur:
                logger.info(f"Creating {table_name} table")
                cur.execute(command)
    except psycopg.errors.OperationalError as e:
        logger.error(f"Error on {table_name} table creation")
        logger.error(e)


def create_users_table(user_db_name: str) -> None:
    create_wrapper(user_db_name, """create table IF NOT EXISTS users
(
    user_id       int          not null
        constraint users_pk
            primary key,
    chat_id       int  not null,
    first_name    text not null,
    last_name     text,
    tournament_id int,
    money         numeric       not null,
    foreign key (tournament_id)
    references tournaments (tournament_id)
);""", "users")


def create_tournaments_table(tournaments_db_name: str) -> None:
    create_wrapper(tournaments_db_name, """create table IF NOT EXISTS tournaments  
(
    tournament_id int                     not null
        constraint tournaments_pk
            primary key,
    start_time    timestamp               not null,
    end_time      timestamp               not null,
    is_ended      bool      default false not null,
    is_started    bool      default false not null,
    code          text      default null
);

""", "tournaments")


def create_longs_table(db_name: str) -> None:
    create_wrapper(db_name, '''create table if not exists longs
(
    user_id       int  not null
        constraint longs_users_user_id_fk
            references users,
    tournament_id int  not null
        constraint longs_tournaments_tournament_id_fk
            references tournaments,
    symbol        text not null,
    amount        int  not null,
    constraint longs_pk
        unique (user_id, tournament_id, symbol)
);''', 'longs')


def create_shorts_table(db_name: str) -> None:
    create_wrapper(db_name, '''create table if not exists shorts
(
    user_id       int       not null
        constraint shorts_users_user_id_fk
            references users,
    tournament_id int       not null
        constraint shorts_tournaments_tournament_id_fk
            references tournaments,
    symbol        text      not null,
    amount        int       not null,
    buy_date      timestamp not null,
    constraint shorts_ok
        unique (user_id, tournament_id, symbol, buy_date)
);''', 'shorts')


def init_databases(db_name: str) -> None:
    create_tournaments_table(db_name)
    create_users_table(db_name)
    create_longs_table(db_name)
    create_shorts_table(db_name)
