from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    balance = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

    bookings = relationship("Booking", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class PC(Base):
    __tablename__ = "pcs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String) # Standard, VIP, Bootcamp
    hourly_rate = Column(Float)

    bookings = relationship("Booking", back_populates="pc")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pc_id = Column(Integer, ForeignKey("pcs.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_price = Column(Float)

    user = relationship("User", back_populates="bookings")
    pc = relationship("PC", back_populates="bookings")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(String) # deposit, booking
    timestamp = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="transactions")
