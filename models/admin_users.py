from sqlalchemy import Column, Integer, String
from utils import Base


class AdminUsers(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
