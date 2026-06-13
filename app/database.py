from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://diplom:7896@127.0.0.1/dip")

# Fix for potential UnicodeDecodeError on Windows when system locale is not UTF-8
if os.name == 'nt':
    os.environ["PGCLIENTENCODING"] = "UTF8"
    # Force English error messages from PostgreSQL to avoid decoding issues
    os.environ["LC_ALL"] = "C"

# Use check_same_thread: False for SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
