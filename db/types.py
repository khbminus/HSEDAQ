from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass(order=True)
class User:
    user_id: int
    chat_id: int
    first_name: str
    last_name: Optional[str] = None
    tournament_id: Optional[int] = None
    money: float = 1000


@dataclass
class Tournament:
    tournament_id: int
    start_time: datetime
    end_time: datetime
    is_ended: bool = False
    is_started: bool = False


@dataclass
class Long:
    user_id: int
    tournament_id: int
    symbol: str
    amount: int


@dataclass
class Short:
    user_id: int
    tournament_id: int
    symbol: str
    amount: int
    buy_date: datetime
