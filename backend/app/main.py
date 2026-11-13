
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas


# DATABASE SETUP
Base.metadata.create_all(bind=engine)


# FASTAPI APP
app = FastAPI(
    title="CampusBite API",
    description="Restaurant Ordering and Delivery Platform",
    version="1.0.0"
)


# JWT CONFIGURATION
SECRET_KEY = "campusbite-development-secret-change-before-submission"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer(auto_error=False)


# PASSWORD FUNCTIONS
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# JWT TOKEN FUNCTION
def create_access_token(user_email: str, user_role: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_email,
        "role": user_role,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# AUTHENTICATION FUNCTION
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please login first"
        )

    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# ROLE CHECK FUNCTION
def require_role(*allowed_roles):
    def role_checker(
        current_user: models.User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )
        return current_user

    return role_checker


# HOME
@app.get("/")
def home():
    return {"message": "Welcome to CampusBite!"}


# REGISTER - ONLY ONE REGISTER API
@app.post("/register")
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    allowed_roles = [
        "customer",
        "restaurant_owner",
        "delivery_partner"
    ]

    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be at most 72 bytes"
        )

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }


# LOGIN
@app.post("/login")
def login(
    data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user.email,
        user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


# PROTECTED PROFILE
@app.get("/me")
def get_my_profile(
    current_user: models.User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


# GET USERS
@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# CREATE RESTAURANT
@app.post("/restaurants")
def create_restaurant(
    data: schemas.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("restaurant_owner")
    )
):
    if data.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create your own restaurant"
        )

    restaurant = models.Restaurant(**data.model_dump())

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant


# GET RESTAURANTS
@app.get("/restaurants")
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(models.Restaurant).all()


# CREATE MENU ITEM
@app.post("/menu")
def create_menu_item(
    data: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("restaurant_owner")
    )
):
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == data.restaurant_id,
        models.Restaurant.owner_id == current_user.id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found or not owned by you"
        )

    item = models.MenuItem(**data.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


# GET MENU
@app.get("/menu/{restaurant_id}")
def get_menu(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.MenuItem).filter(
        models.MenuItem.restaurant_id == restaurant_id
    ).all()


# DELETE MENU ITEM
@app.delete("/menu/{item_id}")
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("restaurant_owner")
    )
):
    item = db.query(models.MenuItem).join(
        models.Restaurant
    ).filter(
        models.MenuItem.id == item_id,
        models.Restaurant.owner_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    db.delete(item)
    db.commit()

    return {"message": "Menu item deleted successfully"}


# CREATE ORDER
@app.post("/orders")
def create_order(
    data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role("customer")
    )
):
    if data.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only place your own order"
        )

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Order must contain items"
        )

    total = 0
    order_items = []

    for requested_item in data.items:
        if requested_item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero"
            )

        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == requested_item.menu_item_id,
            models.MenuItem.is_available == True
        ).first()

        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail="Available menu item not found"
            )

        total += menu_item.price * requested_item.quantity

        order_items.append(
            models.OrderItem(
                menu_item_id=menu_item.id,
                quantity=requested_item.quantity,
                unit_price=menu_item.price
            )
        )

    order = models.Order(
        customer_id=current_user.id,
        delivery_address=data.delivery_address,
        status="PLACED",
        payment_status="mock_paid",
        total_amount=total,
        items=order_items
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    payment = models.PaymentLedger(
        order_id=order.id,
        amount=total,
        transaction_type="payment",
        payment_status="mock_paid"
    )

    db.add(payment)
    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "total_amount": order.total_amount
    }


# GET ALL ORDERS
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


# GET SINGLE ORDER
@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if (
        current_user.role == "customer"
        and order.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if (
        current_user.role == "delivery_partner"
        and order.delivery_partner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return order


# UPDATE ORDER STATUS
@app.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if current_user.role == "restaurant_owner":
        restaurant = db.query(models.Restaurant).filter(
            models.Restaurant.owner_id == current_user.id
        ).first()

        if not restaurant:
            raise HTTPException(
                status_code=403,
                detail="Restaurant not found"
            )

        menu_item = db.query(models.OrderItem).join(
            models.MenuItem
        ).filter(
            models.OrderItem.order_id == order_id,
            models.MenuItem.restaurant_id == restaurant.id
        ).first()

        if not menu_item:
            raise HTTPException(
                status_code=403,
                detail="This order does not belong to your restaurant"
            )

    elif current_user.role == "delivery_partner":
        if order.delivery_partner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="This order is not assigned to you"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    allowed_transitions = {
        "PLACED": ["ACCEPTED", "CANCELLED"],
        "ACCEPTED": ["PREPARING"],
        "PREPARING": ["READY"],
        "READY": ["ASSIGNED"],
        "ASSIGNED": ["OUT_FOR_DELIVERY"],
        "OUT_FOR_DELIVERY": ["DELIVERED"]
    }

    if status not in allowed_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {order.status} to {status}"
        )

    order.status = status
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "status": order.status
    }
