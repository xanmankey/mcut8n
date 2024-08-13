from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from utils import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date_time = Column(String, nullable=False)
    img = Column(String, nullable=False)
    suggested = Column(Boolean)
    rating = Column(Integer, default=0)
