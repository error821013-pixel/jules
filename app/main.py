from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from . import models, schemas, crud, auth, database
from .database import engine, get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    models.Base.metadata.create_all(bind=engine)

    # Seed data
    db = next(database.get_db())
    try:
        if not crud.get_pcs(db):
            crud.create_pc(db, schemas.PCBase(name="PC 1 (Standard)", category="Standard", hourly_rate=50.0))
            crud.create_pc(db, schemas.PCBase(name="PC 2 (Standard)", category="Standard", hourly_rate=50.0))
            crud.create_pc(db, schemas.PCBase(name="PC 3 (VIP)", category="VIP", hourly_rate=100.0))
            crud.create_pc(db, schemas.PCBase(name="PC 4 (Bootcamp)", category="Bootcamp", hourly_rate=150.0))

        if not crud.get_user_by_username(db, "admin"):
            admin_user = models.User(
                username="admin",
                hashed_password=auth.get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()

    yield
    # Shutdown logic (if any)

app = FastAPI(title="Gaming Club", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    payload = auth.decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = auth.decode_token(token)
        username = payload.get("sub")
        return crud.get_user_by_username(db, username=username)
    except:
        return None

# API Routes
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Page Routes
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/location", response_class=HTMLResponse)
async def read_location(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse("location.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")

    pcs = crud.get_pcs(db)
    bookings = crud.get_user_bookings(db, user.id)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "pcs": pcs,
        "bookings": bookings
    })

@app.post("/bookings/", response_model=schemas.Booking)
async def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_booking = crud.create_booking(db, booking, current_user.id)
    if not db_booking:
        raise HTTPException(status_code=400, detail="Booking failed. Check balance or PC availability.")
    return db_booking

@app.post("/deposit")
async def deposit(
    amount: float = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.deposit_balance(db, current_user.id, amount)
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_optional(request, db)
    if not user or not user.is_admin:
        return HTMLResponse(content="Access Denied", status_code=403)

    stats = crud.get_admin_stats(db)
    current_bookings = crud.get_current_bookings(db)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "current_bookings": current_bookings,
        "now": datetime.utcnow()
    })

@app.get("/pcs/", response_model=List[schemas.PC])
def read_pcs(db: Session = Depends(get_db)):
    return crud.get_pcs(db)
