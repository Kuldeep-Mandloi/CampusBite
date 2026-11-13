
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class RestaurantCreate(BaseModel):
    name: str
    location: str
    owner_id: int


class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    restaurant_id: int


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int
    delivery_address: str
    items: list[OrderItemCreate]
