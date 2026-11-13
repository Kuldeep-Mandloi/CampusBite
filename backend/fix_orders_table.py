
from sqlalchemy import text
from app.database import engine

with engine.begin() as connection:
    connection.execute(text(
        "ALTER TABLE orders ADD COLUMN created_at DATETIME"
    ))

    connection.execute(text(
        "UPDATE orders SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
    ))

print("created_at column added successfully!")
