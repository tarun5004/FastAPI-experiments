from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base


#database setup
DATABASE_URL = "sqlite:///./transactions.db"
engine = create_engine(DATABASE_URL, echo=True) # echo=True for logging SQL queries
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Create a configured "Session" class autocommit and autoflush are set to False meaning changes are not saved until we explicitly commit them
db = Sessionlocal()  # Create a Session instance
Base = declarative_base()  # Base class for our classes definitions

# Create Models
