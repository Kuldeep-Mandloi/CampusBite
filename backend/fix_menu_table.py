
from sqlalchemy import inspect, text
from app.database import engine

inspector = inspect(engine)

columns = [
    column["name"]
    for column in inspector.get_columns("orders")
]

with engine.begin() as connection:
    if "total_amount" not in columns:
        connection.execute(
            text(
                "ALTER TABLE orders "
                "ADD COLUMN total_amount FLOAT NOT NULL DEFAULT 0.0"
            )
        )
        print("Added: total_amount")
    else:
        print("Already exists: total_amount")

print("Orders migration completed!")

print("Final orders columns:")
for column in inspect(engine).get_columns("orders"):
    print(column["name"])
