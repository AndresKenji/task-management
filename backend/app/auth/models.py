from enum import unique
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from database.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    creation_date = Column(Date, nullable=False)
    disable_date = Column(Date, nullable=True)
    last_login = Column(DateTime, nullable=True)
