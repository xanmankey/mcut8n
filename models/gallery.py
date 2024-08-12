from sqlalchemy import Column, Integer, BLOB, ForeignKey
from sqlalchemy.orm import relationship

# from models.event import Event

from utils import Base


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True)
    img = Column(BLOB)
    event_id = Column(ForeignKey("events.id"))

    # event = relationship("Event", back_populates="gallery")
