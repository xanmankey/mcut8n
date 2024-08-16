from sqlalchemy import Column, DateTime, Integer, String, Boolean, LargeBinary
from utils import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=True)
    img = Column(String, nullable=False)
    suggested = Column(Boolean)
    completed = Column(Boolean, default=False)
    rating = Column(Integer, default=0)
