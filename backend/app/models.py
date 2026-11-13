
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey,
    DateTime, Text, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, default="customer", nullable=False)
    password_hash = Column(String, nullable=True)

    restaurants = relationship("Restaurant", back_populates="owner")
    customer_orders = relationship(
        "Order", back_populates="customer",
        foreign_keys="Order.customer_id"
    )
    delivery_orders = relationship(
        "Order", back_populates="delivery_partner",
        foreign_keys="Order.delivery_partner_id"
    )


# 2. RESTAURANTS TABLE
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="restaurants")
    menu_items = relationship("MenuItem", back_populates="restaurant")


# 3. MENU ITEMS TABLE
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )

    restaurant = relationship("Restaurant", back_populates="menu_items")


# 4. ORDERS TABLE
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PLACED", nullable=False)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="pending")

    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    delivery_address = Column(String, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship(
        "User", back_populates="customer_orders",
        foreign_keys=[customer_id]
    )
    delivery_partner = relationship(
        "User", back_populates="delivery_orders",
        foreign_keys=[delivery_partner_id]
    )
    items = relationship("OrderItem", back_populates="order")


# 5. ORDER ITEMS TABLE
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")


# 6. REVIEWS TABLE
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, default="")
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)


# 7. PAYMENT LEDGER TABLE
class PaymentLedger(Base):
    __tablename__ = "payment_ledger"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # payment/refund
    payment_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 8. RETURN REQUESTS TABLE
class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer, ForeignKey("orders.id"), unique=True, nullable=False
    )
    reason = Column(Text, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 9. ADMIN REMINDER LOGS TABLE
class AdminReminderLog(Base):
    __tablename__ = "admin_reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
