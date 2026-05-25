from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    balance: float
    points: int
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)

class PCBase(BaseModel):
    name: str
    category: str
    hourly_rate: float

class PC(PCBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookingBase(BaseModel):
    pc_id: int
    start_time: datetime
    end_time: datetime

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    total_price: float
    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    amount: float
    type: str

class Transaction(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class AdminStats(BaseModel):
    average_check: float
    total_revenue: float
    current_bookings_count: int
