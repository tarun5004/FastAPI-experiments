from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from .database import Base # Importing Base from database module

class User(Base):
    __tablename__ = "users"  # Table name in the database
    id = Column(Integer, primary_key=True, index=True)  # Primary key column
    name = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)