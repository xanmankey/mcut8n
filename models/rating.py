from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# from models.event import Event

from utils import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    score = Column(Integer, default=0)
    event_id = Column(Integer, ForeignKey("events.id"))

    # event = relationship("Event", back_populates="ratings")
