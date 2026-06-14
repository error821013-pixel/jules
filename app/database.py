import os

# Mandatory fix for UnicodeDecodeError on Windows with non-UTF8 locale
# These MUST be set before importing any database-related modules
if os.name == 'nt':
    os.environ["PGCLIENTENCODING"] = "UTF8"
    os.environ["LC_ALL"] = "C"
    os.environ["LC_MESSAGES"] = "C"
    os.environ["LANG"] = "en_US.UTF-8"
    os.environ["PYTHONIOENCODING"] = "utf-8"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Using 127.0.0.1 to avoid common IPv6 resolution issues on Windows
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://diplom:7896@127.0.0.1:5432/dip")

# Explicitly setting client_encoding to utf8
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"client_encoding": "utf8"}

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
