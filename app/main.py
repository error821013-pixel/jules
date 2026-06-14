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
    # Startup: create tables and seed data
    db = None
    try:
        models.Base.metadata.create_all(bind=engine)

        db = next(database.get_db())
        if not crud.get_pcs(db):
            # Standard: 2 rooms x 10 PCs
            for r in range(1, 3):
                for i in range(1, 11):
                    crud.create_pc(db, schemas.PCBase(
                        name=f"Standard PC {i} (Room {r})",
                        category="Standard",
                        room=f"Standard Room {r}",
                        hourly_rate=100.0
                    ))

            # VIP: 4 rooms x 5 PCs (User requested 20 total)
            for r in range(1, 5):
                for i in range(1, 6):
                    crud.create_pc(db, schemas.PCBase(
                        name=f"VIP PC {i} (Room {r})",
                        category="VIP",
                        room=f"VIP Room {r}",
                        hourly_rate=300.0
                    ))

            # Bootcamp: 2 rooms x 3 PCs
            for r in range(1, 3):
                for i in range(1, 4):
                    crud.create_pc(db, schemas.PCBase(
                        name=f"Bootcamp PC {i} (Room {r})",
                        category="Bootcamp",
                        room=f"Bootcamp Room {r}",
                        hourly_rate=500.0
                    ))

        if not crud.get_user_by_username(db, "admin"):
            admin_user = models.User(
                username="admin",
                hashed_password=auth.get_password_hash("admin123"),
                balance=10000.0,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()

        if not crud.get_user_by_username(db, "gamer"):
            # Create a test active user
            test_user = models.User(
                username="gamer",
                hashed_password=auth.get_password_hash("pass123"),
                balance=5000.0,
                is_admin=False
            )
            db.add(test_user)
            db.commit()
            print("[INFO] Создан тестовый аккаунт: gamer / pass123")

        print("[SUCCESS] База данных PostgreSQL успешно подключена!")
    except Exception as e:
        print("\n" + "!"*60)
        print("ВНИМАНИЕ: ОШИБКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ!")
        print("-" * 60)
        print("Сайт будет работать в ограниченном режиме.")
        print("Пожалуйста, убедитесь, что:")
        print("1. В pgAdmin создана база данных с именем: dip")
        print("2. Создан пользователь: diplom с паролем: 7896")
        print("3. У пользователя diplom есть права на базу dip")
        print("-" * 60)
        print("Техническая информация об ошибке (может быть нечитаемой на Windows):")
        try:
            print(f"Тип ошибки: {type(e).__name__}")
        except:
            pass
        print("!"*60 + "\n")
    finally:
        if db:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    payload = auth.decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
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
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Page Routes
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "index.html", {"user": user})

@app.get("/location", response_class=HTMLResponse)
async def read_location(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "location.html", {"user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse(request, "login.html", {})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login")

    pcs = crud.get_pcs_with_status(db)
    bookings = crud.get_user_bookings(db, user.id)
    transactions = crud.get_user_transactions(db, user.id)

    # Group PCs by zone and room for the map
    zones = {}
    for pc in pcs:
        zone = pc['category']
        room = pc['room']
        if zone not in zones:
            zones[zone] = {}
        if room not in zones[zone]:
            zones[zone][room] = []
        zones[zone][room].append(pc)

    return templates.TemplateResponse(request, "profile.html", {
        "user": user,
        "zones": zones,
        "bookings": bookings,
        "transactions": transactions
    })

@app.post("/bookings/", response_model=schemas.Booking)
async def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_booking = crud.create_booking(db, booking, current_user.id)
    if not db_booking:
        raise HTTPException(status_code=400, detail="Ошибка бронирования. Проверьте баланс или доступность ПК.")
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
        return HTMLResponse(content="Доступ запрещен", status_code=403)

    stats = crud.get_admin_stats(db)
    current_bookings = crud.get_current_bookings(db)
    return templates.TemplateResponse(request, "admin.html", {
        "user": user,
        "stats": stats,
        "current_bookings": current_bookings,
        "now": datetime.utcnow()
    })

@app.get("/pcs/", response_model=List[schemas.PC])
def read_pcs(db: Session = Depends(get_db)):
    return crud.get_pcs(db)

@app.post("/pcs/", response_model=schemas.PC)
def create_pc(pc: schemas.PCBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Не авторизован")
    return crud.create_pc(db=db, pc=pc)

@app.delete("/pcs/{pc_id}")
def delete_pc(pc_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Не авторизован")
    if not crud.delete_pc(db=db, pc_id=pc_id):
        raise HTTPException(status_code=404, detail="ПК не найден")
    return {"message": "ПК удален"}

@app.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_booking(db, booking_id, current_user.id, current_user.is_admin)
    if not success:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или недостаточно прав для удаления")
    return {"message": "Бронирование удалено"}
