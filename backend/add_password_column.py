
from sqlalchemy import inspect, text
from app.database import engine

columns = [
    column["name"]
    for column in inspect(engine).get_columns("users")
]

if "password_hash" not in columns:
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE users ADD COLUMN password_hash VARCHAR")
        )
    print("password_hash column added successfully!")
else:
    print("password_hash column already exists!")