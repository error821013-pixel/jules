import os
import sys

# Windows Unicode Fix
if os.name == 'nt':
    os.environ["PGCLIENTENCODING"] = "UTF8"

from sqlalchemy import create_engine, text
from app import models, auth, schemas, database

def fix():
    print("--- ЗАПУСК ПОЛНОГО ИСПРАВЛЕНИЯ БАЗЫ ДАННЫХ (46 ПК, нумерация 1-46) ---")

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:7896@127.0.0.1:5432/dip")
    engine = create_engine(db_url)
    is_sqlite = db_url.startswith("sqlite")

    try:
        with engine.connect() as conn:
            print(f"1. Подключение к {db_url}... ОК")

            # Drop everything to start fresh
            print("2. Очистка старых данных...")
            tables = ["bookings", "transactions", "pcs", "users"]
            for table in tables:
                if is_sqlite:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                else:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
            print("   ОК")

            # Create everything according to current models
            print("3. Создание структуры таблиц...")
            models.Base.metadata.create_all(bind=engine)
            print("   ОК")

            # Seed data
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            print("4. Создание аккаунтов (admin, gamer)...")
            admin = models.User(
                username="admin",
                hashed_password=auth.get_password_hash("admin123"),
                balance=10000.0,
                is_admin=True
            )
            gamer = models.User(
                username="gamer",
                hashed_password=auth.get_password_hash("pass123"),
                balance=5000.0,
                is_admin=False
            )
            db.add(admin)
            db.add(gamer)

            print("5. Наполнение клуба компьютерами (46 шт, номера 1-46)...")
            pc_counter = 1

            # Standard: 2 rooms x 10 PCs = 20
            for r in range(1, 3):
                for i in range(1, 11):
                    db.add(models.PC(
                        name=f"{pc_counter}",
                        category="Standard",
                        room=f"Standard Room {r}",
                        hourly_rate=100.0
                    ))
                    pc_counter += 1

            # VIP: 4 rooms x 5 PCs = 20
            for r in range(1, 5):
                for i in range(1, 6):
                    db.add(models.PC(
                        name=f"{pc_counter}",
                        category="VIP",
                        room=f"VIP Room {r}",
                        hourly_rate=300.0
                    ))
                    pc_counter += 1

            # Bootcamp: 2 rooms x 3 PCs = 6
            for r in range(1, 3):
                for i in range(1, 4):
                    db.add(models.PC(
                        name=f"{pc_counter}",
                        category="Bootcamp",
                        room=f"Bootcamp Room {r}",
                        hourly_rate=500.0
                    ))
                    pc_counter += 1

            db.commit()
            db.close()
            print(f"   ОК (Добавлено {pc_counter-1} ПК)")

            print("\n" + "="*30)
            print("ВСЁ ГОТОВО! Теперь запустите сайт и проверьте карту клуба.")
            print("="*30)

    except Exception as e:
        print(f"\n[ОШИБКА]: {e}")
        if not is_sqlite:
            print("\nПроверьте соединение с PostgreSQL в pgAdmin!")

if __name__ == "__main__":
    fix()
