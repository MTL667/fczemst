from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class Category(str, enum.Enum):
    TRAINER = "Trainer"
    U13 = "U13"
    U15 = "U15"
    U16 = "U16"
    U17 = "U17"


class Day(str, enum.Enum):
    SATURDAY = "zaterdag"
    SUNDAY = "zondag"


SANDWICH_OPTIONS = [
    "pistolet kaas",
    "pistolet hesp",
    "pistolet kip",
    "pistolet salami",
    "sandwich kaas",
    "sandwich hesp",
    "sandwich kip",
    "sandwich salami",
]

FRUIT_OPTIONS = [
    "appel",
    "banaan",
]


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)

    orders = relationship("Order", back_populates="player", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    day = Column(String, nullable=False)
    sandwich_1 = Column(String, nullable=False)
    sandwich_2 = Column(String, nullable=False)
    sandwich_3 = Column(String, nullable=False)
    fruit = Column(String, nullable=False)

    player = relationship("Player", back_populates="orders")

    __table_args__ = (
        UniqueConstraint("player_id", "day", name="uq_player_day"),
    )
