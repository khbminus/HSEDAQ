from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(order=True)
class User:
    user_id: int
    chat_id: int
    first_name: str
    last_name: Optional[str] = None
    tournament_id: int = -1
    money: Decimal = 1000
    sketch_query: Optional[str] = None
    sketch_text: Optional[str] = None
    last_message_id: Optional[int] = None


@dataclass
class Tournament:
    tournament_id: int
    start_time: datetime
    end_time: datetime
    is_ended: bool = False
    is_started: bool = False
    code: Optional[str] = None


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
