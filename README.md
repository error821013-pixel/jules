# Gaming Club Management System

A full-fledged web application for a computer/gaming club featuring user authentication, PC booking, balance management, and an admin dashboard.

## Project Structure
```
.
├── app/
│   ├── static/          # CSS and JS files
│   ├── templates/       # HTML templates
│   ├── auth.py          # Authentication logic
│   ├── crud.py          # Database operations
│   ├── database.py      # Database connection
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy models
│   └── schemas.py       # Pydantic schemas
├── requirements.txt     # Python dependencies
└── README.md            # Documentation and SQL queries
```

## Setup and Run Instructions

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    To connect a PostgreSQL database, set the `DATABASE_URL` environment variable:
    ```bash
    export DATABASE_URL="postgresql://user:password@host:port/dbname"
    ```
    If not set, it defaults to `sqlite:///./club.db` for local testing.

3.  **Database Migration (PostgreSQL):**
    The application will automatically create tables and seed initial data upon the first successful connection. You can also manually run the queries in `schema.sql`.

4.  **Run the application:**
    ```bash
    python run.py
    ```

## PostgreSQL Setup & Troubleshooting

### How to create the database:
1.  Open **pgAdmin 4**.
2.  Right-click on **Databases** -> **Create** -> **Database...**
3.  Name it: `dip`
4.  Ensure the owner is `postgres`.
5.  If you need to reset the password for the `postgres` user to `7896`:
    -   Right-click on your Server (e.g., "PostgreSQL 16") -> **Properties** -> **Connection**.
    -   Or use the SQL tool: `ALTER USER postgres WITH PASSWORD '7896';`

### Troubleshooting "Connection Error":
*   **Windows Encoding:** If you see strange characters in the console, the app is already configured to fix this via environment variables in `run.py`.
*   **Password:** Double-check that your PostgreSQL password is exactly `7896`. If it's different, you must change it in `app/database.py`.
*   **Port:** Default is `5432`. If your Postgres is on a different port (e.g., `5433`), update the connection string.

## Raw SQL Queries (PostgreSQL)

### Table Creation
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    balance FLOAT DEFAULT 0.0,
    points INTEGER DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE pcs (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    category VARCHAR NOT NULL, -- Standard, VIP, Bootcamp
    room VARCHAR DEFAULT 'Main',
    hourly_rate FLOAT NOT NULL
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pc_id INTEGER REFERENCES pcs(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    total_price FLOAT NOT NULL
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount FLOAT NOT NULL,
    type VARCHAR NOT NULL, -- deposit, booking
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### CRUD Operations

**Add a user:**
```sql
INSERT INTO users (username, hashed_password, balance, points, is_admin)
VALUES ('johndoe', 'hashed_pass_here', 0.0, 0, FALSE);
```

**Booking a PC:**
```sql
INSERT INTO bookings (user_id, pc_id, start_time, end_time, total_price)
VALUES (1, 5, '2023-10-27 14:00:00', '2023-10-27 16:00:00', 30.0);

UPDATE users SET balance = balance - 30.0 WHERE id = 1;
```

**Updating balances:**
```sql
UPDATE users SET balance = balance + 100.0 WHERE id = 1;
```

**Admin Analytical Queries:**

*   **Average Check (Average Order Value):**
    ```sql
    SELECT AVG(total_price) FROM bookings WHERE start_time BETWEEN '2023-10-01' AND '2023-10-31';
    ```

*   **Total Revenue:**
    ```sql
    SELECT SUM(total_price) FROM bookings WHERE start_time BETWEEN '2023-10-01' AND '2023-10-31';
    ```

*   **Current Occupied PCs:**
    ```sql
    SELECT p.name, b.end_time
    FROM bookings b
    JOIN pcs p ON b.pc_id = p.id
    WHERE NOW() BETWEEN b.start_time AND b.end_time;
    ```
