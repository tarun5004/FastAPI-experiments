from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # SQLite specific means only one thread can access the database at a time
)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Create a configured "Session" class
Base = declarative_base()  # Base class for our classes definitions

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()