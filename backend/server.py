from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Enums
class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ShippingMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Order Item Model
class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    selected_size: str
    selected_color: str
    image: Optional[str] = None

# Customer Information Model
class CustomerInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

# Shipping Address Model
class ShippingAddress(BaseModel):
    address: str
    city: str
    postal_code: str
    country: str = "Israel"

# Payment Information Model (for mock)
class PaymentInfo(BaseModel):
    card_last_four: str
    card_name: str
    payment_method: str = "credit_card"

# Order Create Model
class OrderCreate(BaseModel):
    customer_info: CustomerInfo
    shipping_address: ShippingAddress
    items: List[OrderItem]
    shipping_method: ShippingMethod
    shipping_cost: float
    subtotal: float
    total: float
    payment_info: PaymentInfo

# Order Response Model
class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = Field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    customer_info: CustomerInfo
    shipping_address: ShippingAddress
    items: List[OrderItem]
    shipping_method: ShippingMethod
    shipping_cost: float
    subtotal: float
    total: float
    payment_info: PaymentInfo
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    payment_transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None

# Order Update Model
class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    payment_transaction_id: Optional[str] = None

# Payment Mock Model
class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    card_number: str
    card_name: str
    expiry_date: str
    cvv: str

class PaymentResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: str
    order_id: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()