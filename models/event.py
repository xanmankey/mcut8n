from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
from utils import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    img = Column(LargeBinary)
    suggested = Column(Boolean)
    rating = Column(Integer, default=0)
