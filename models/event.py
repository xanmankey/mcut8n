from sqlalchemy import Column, DateTime, Integer, String, Boolean, LargeBinary, Enum
from utils import Base
from enum import Enum as Enumerate


class Color(Enumerate):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    BLACK = "black"
    WHITE = "white"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    logistics = Column(String, nullable=True)
    description = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=True)
    # end_time = Column(DateTime, nullable=True)
    img = Column(String, nullable=False)
    suggested = Column(Boolean)
    completed = Column(Boolean, default=False)
    rating = Column(Integer, default=0)
    title_text_color = Column(Enum(Color), nullable=True)
    info_text_color = Column(Enum(Color), nullable=True)
