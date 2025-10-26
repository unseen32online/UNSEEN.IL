from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Order Status Enum
class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_RECEIVED = "payment_received"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Product Item in Order
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    size: str
    color: str
    image: Optional[str] = None

# Customer Information
class CustomerInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    postal_code: str
    country: str = "Israel"

# Order Model
class Order(BaseModel):
    id: Optional[str] = None
    order_number: Optional[str] = None
    customer: CustomerInfo
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float
    total: float
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    payment_method: str = "HYP"
    payment_status: str = "pending"
    payment_transaction_id: Optional[str] = None
    shipping_method: str = "standard"
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Order Create Request
class OrderCreate(BaseModel):
    customer: CustomerInfo
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float
    total: float
    shipping_method: str = "standard"
    notes: Optional[str] = None

# Order Update Request
class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[str] = None
    payment_transaction_id: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

# Admin User Model
class AdminUser(BaseModel):
    username: str
    password: str

# Order Statistics
class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    total_revenue: float
    today_orders: int
    today_revenue: float
