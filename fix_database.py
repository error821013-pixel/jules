import os
import sys

# Windows Unicode Fix
if os.name == 'nt':
    os.environ["PGCLIENTENCODING"] = "UTF8"

from sqlalchemy import create_engine, text
from app import models, auth, schemas, database

def fix():
    print("--- ЗАПУСК ИСПРАВЛЕНИЯ БАЗЫ ДАННЫХ ---")

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:7896@127.0.0.1:5432/dip")
    engine = create_engine(db_url)
    is_sqlite = db_url.startswith("sqlite")

    try:
        with engine.connect() as conn:
            print(f"1. Подключение к {db_url}... ОК")

            # Drop everything to start fresh
            print("2. Удаление старых таблиц...")
            tables = ["bookings", "transactions", "pcs", "users"]
            for table in tables:
                if is_sqlite:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                else:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
            print("   ОК")

            # Create everything according to current models
            print("3. Создание новых таблиц...")
            models.Base.metadata.create_all(bind=engine)
            print("   ОК")

            # Seed gamer
            print("4. Создание пользователя gamer (пароль: pass123)...")
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            gamer = models.User(
                username="gamer",
                hashed_password=auth.get_password_hash("pass123"),
                balance=5000.0,
                is_admin=False
            )
            db.add(gamer)

            # Seed some PCs
            print("5. Добавление компьютеров...")
            pc = models.PC(name="Standard PC 1", category="Standard", room="Room 1", hourly_rate=100.0)
            db.add(pc)

            db.commit()
            db.close()
            print("   ОК")

            print("\n" + "="*30)
            print("ВСЁ ГОТОВО! Теперь запустите python run.py и войдите под gamer / pass123")
            print("="*30)

    except Exception as e:
        print(f"\n[ОШИБКА]: {e}")
        if not is_sqlite:
            print("\nПохоже, база 'dip' не найдена или пароль '7896' не подходит.")
            print("Проверьте настройки в pgAdmin!")

if __name__ == "__main__":
    fix()
