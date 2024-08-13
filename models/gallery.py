from sqlalchemy import Column, Integer, BLOB, ForeignKey, String
from sqlalchemy.orm import relationship

# from models.event import Event

from utils import Base


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True)
    img = Column(String, nullable=False)
    event_id = Column(ForeignKey("events.id"))

    # event = relationship("Event", back_populates="gallery")
