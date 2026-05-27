from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime
from sqlalchemy import func, or_, and_

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_pcs(db: Session):
    return db.query(models.PC).all()

def create_pc(db: Session, pc: schemas.PCBase):
    db_pc = models.PC(**pc.model_dump())
    db.add(db_pc)
    db.commit()
    db.refresh(db_pc)
    return db_pc

def create_booking(db: Session, booking: schemas.BookingCreate, user_id: int):
    # 1. Validate duration
    if booking.end_time <= booking.start_time:
        return None

    # 2. Check PC existence
    pc = db.query(models.PC).filter(models.PC.id == booking.pc_id).first()
    if not pc:
        return None

    # 3. Check for overlapping bookings for this PC
    overlap = db.query(models.Booking).filter(
        models.Booking.pc_id == booking.pc_id,
        or_(
            and_(models.Booking.start_time <= booking.start_time, models.Booking.end_time > booking.start_time),
            and_(models.Booking.start_time < booking.end_time, models.Booking.end_time >= booking.end_time),
            and_(models.Booking.start_time >= booking.start_time, models.Booking.end_time <= booking.end_time)
        )
    ).first()

    if overlap:
        return None

    duration = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = duration * pc.hourly_rate

    # 4. Check user balance
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.balance < total_price:
        return None

    # Deduct balance
    user.balance -= total_price
    # Add loyalty points (e.g. 1 point per 10 currency)
    user.points += int(total_price / 10)

    db_booking = models.Booking(
        **booking.model_dump(),
        user_id=user_id,
        total_price=total_price
    )

    db_transaction = models.Transaction(
        user_id=user_id,
        amount=-total_price,
        type="booking"
    )

    db.add(db_booking)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_user_bookings(db: Session, user_id: int):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()

def get_current_bookings(db: Session):
    now = datetime.utcnow()
    return db.query(models.Booking).filter(
        models.Booking.start_time <= now,
        models.Booking.end_time >= now
    ).all()

def get_admin_stats(db: Session):
    total_revenue = db.query(func.sum(models.Booking.total_price)).scalar() or 0.0
    avg_check = db.query(func.avg(models.Booking.total_price)).scalar() or 0.0
    current_bookings_count = len(get_current_bookings(db))

    return {
        "total_revenue": total_revenue,
        "average_check": avg_check,
        "current_bookings_count": current_bookings_count
    }

def deposit_balance(db: Session, user_id: int, amount: float):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.balance += amount
    db_transaction = models.Transaction(
        user_id=user_id,
        amount=amount,
        type="deposit"
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(user)
    return user
