from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    tournament_id: Optional[int] = None
    money: float = 1000  # TODO: probably should be float?


@dataclass
class Tournament:
    tournament_id: int
    start_time: datetime
    end_time: datetime
    is_ended: bool


@dataclass
class Stock:
    ticker: str
    fetch_date: datetime
    price: float
