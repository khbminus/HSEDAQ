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
    first_name    text not null,
    last_name     text,
    tournament_id int,
    money         float8       not null,
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
    is_started    bool      default false not null
);

""", "tournaments")


def create_stocks_table(stocks_db_name: str) -> None:
    create_wrapper(stocks_db_name, """create table if not exists stocks
(
    ticker     text not null,
    fetch_date timestamp   not null,
    price      float8      not null
);
""", "stocks")


def creat_actions_table(actions_db_name: str) -> None:
    create_wrapper(actions_db_name, """create table if not exists actions
(
    user_id       int       not null
        constraint actions_users_user_id_fk
            references users,
    tournament_id int       not null
        constraint actions_tournaments_tournament_id_fk
            references tournaments
            on update restrict on delete restrict,
    buy_type      text      not null,
    ticker        text      not null,
    price         float8    not null,
    timestamp     timestamp not null
);""", 'actions')


def init_databases(db_name: str) -> None:
    create_tournaments_table(db_name)
    create_users_table(db_name)
    create_stocks_table(db_name)
    creat_actions_table(db_name)
