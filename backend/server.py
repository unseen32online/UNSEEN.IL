from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from passlib.context import CryptContext
from jose import JWTError, jwt


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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

# ==================== ORDER MANAGEMENT ENDPOINTS ====================

# Helper function to serialize datetime for MongoDB
def serialize_for_mongo(data: dict) -> dict:
    """Convert datetime objects to ISO strings for MongoDB storage"""
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            data[key] = serialize_for_mongo(value)
        elif isinstance(value, list):
            data[key] = [serialize_for_mongo(item) if isinstance(item, dict) else item for item in value]
    return data

# Helper function to deserialize from MongoDB
def deserialize_from_mongo(data: dict) -> dict:
    """Convert ISO string timestamps back to datetime objects"""
    for key, value in data.items():
        if key in ['created_at', 'updated_at', 'timestamp'] and isinstance(value, str):
            try:
                data[key] = datetime.fromisoformat(value)
            except:
                pass
        elif isinstance(value, dict):
            data[key] = deserialize_from_mongo(value)
        elif isinstance(value, list):
            data[key] = [deserialize_from_mongo(item) if isinstance(item, dict) else item for item in value]
    return data

# Mock Email Service
async def send_order_confirmation_email(order: Order):
    """Mock email service - logs email to console"""
    logger.info(f"""
    ========== ORDER CONFIRMATION EMAIL ==========
    To: {order.customer_info.email}
    Subject: Order Confirmation - {order.order_number}
    
    Dear {order.customer_info.first_name} {order.customer_info.last_name},
    
    Thank you for your order with UNSEEN!
    
    Order Number: {order.order_number}
    Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    Status: {order.status.value}
    
    Items Ordered:
    {chr(10).join([f"  - {item.name} ({item.selected_color}, {item.selected_size}) x{item.quantity} - ₪{item.price * item.quantity:.2f}" for item in order.items])}
    
    Subtotal: ₪{order.subtotal:.2f}
    Shipping: ₪{order.shipping_cost:.2f}
    Total: ₪{order.total:.2f}
    
    Shipping Address:
    {order.shipping_address.address}
    {order.shipping_address.city}, {order.shipping_address.postal_code}
    {order.shipping_address.country}
    
    We will notify you when your order ships.
    
    Thank you for shopping with UNSEEN!
    ==============================================
    """)

# Create Order
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    """Create a new order"""
    try:
        # Create order object
        order = Order(
            customer_info=order_data.customer_info,
            shipping_address=order_data.shipping_address,
            items=order_data.items,
            shipping_method=order_data.shipping_method,
            shipping_cost=order_data.shipping_cost,
            subtotal=order_data.subtotal,
            total=order_data.total,
            payment_info=order_data.payment_info,
            status=OrderStatus.PENDING_PAYMENT
        )
        
        # Convert to dict and serialize datetime to ISO string for MongoDB
        order_dict = order.model_dump()
        order_dict = serialize_for_mongo(order_dict)
        
        # Save to database
        await db.orders.insert_one(order_dict)
        
        # Send confirmation email (mock)
        await send_order_confirmation_email(order)
        
        logger.info(f"Order created successfully: {order.order_number}")
        return order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

# Get Order by ID
@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get order by ID"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = deserialize_from_mongo(order)
    return Order(**order)

# Get Order by Order Number
@api_router.get("/orders/number/{order_number}", response_model=Order)
async def get_order_by_number(order_number: str):
    """Get order by order number"""
    order = await db.orders.find_one({"order_number": order_number}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = deserialize_from_mongo(order)
    return Order(**order)

# List All Orders
@api_router.get("/orders", response_model=List[Order])
async def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_email: Optional[str] = Query(None, description="Filter by customer email"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    skip: int = Query(0, ge=0, description="Number of orders to skip")
):
    """List all orders with optional filters"""
    query = {}
    
    if status:
        query["status"] = status.value
    if customer_email:
        query["customer_info.email"] = customer_email
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    for order in orders:
        order = deserialize_from_mongo(order)
    
    return [Order(**order) for order in orders]

# Update Order Status
@api_router.patch("/orders/{order_id}", response_model=Order)
async def update_order(order_id: str, update_data: OrderUpdate):
    """Update order status and notes"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_fields = {}
    if update_data.status:
        update_fields["status"] = update_data.status.value
    if update_data.notes is not None:
        update_fields["notes"] = update_data.notes
    if update_data.payment_transaction_id:
        update_fields["payment_transaction_id"] = update_data.payment_transaction_id
    
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.orders.update_one({"id": order_id}, {"$set": update_fields})
    
    # Get updated order
    updated_order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    updated_order = deserialize_from_mongo(updated_order)
    
    logger.info(f"Order {order_id} updated successfully")
    return Order(**updated_order)

# Delete Order (Admin only)
@api_router.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    """Delete an order"""
    result = await db.orders.delete_one({"id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    logger.info(f"Order {order_id} deleted successfully")
    return {"message": "Order deleted successfully", "order_id": order_id}

# ==================== PAYMENT MOCK ENDPOINTS ====================

@api_router.post("/payment/process", response_model=PaymentResponse)
async def process_payment(payment_data: PaymentRequest):
    """Mock payment processing endpoint"""
    try:
        # Simulate payment processing
        # In production, this would integrate with HYP payment gateway
        
        # Mock validation
        if not payment_data.card_number or len(payment_data.card_number.replace(" ", "")) < 13:
            return PaymentResponse(
                success=False,
                message="Invalid card number",
                order_id=payment_data.order_id
            )
        
        if not payment_data.cvv or len(payment_data.cvv) < 3:
            return PaymentResponse(
                success=False,
                message="Invalid CVV",
                order_id=payment_data.order_id
            )
        
        # Generate mock transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Update order with payment confirmation
        await db.orders.update_one(
            {"id": payment_data.order_id},
            {
                "$set": {
                    "status": OrderStatus.PAYMENT_CONFIRMED.value,
                    "payment_transaction_id": transaction_id,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Payment processed successfully for order {payment_data.order_id}: {transaction_id}")
        
        return PaymentResponse(
            success=True,
            transaction_id=transaction_id,
            message="Payment processed successfully",
            order_id=payment_data.order_id
        )
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        return PaymentResponse(
            success=False,
            message=f"Payment processing failed: {str(e)}",
            order_id=payment_data.order_id
        )

# ==================== ADMIN DASHBOARD ENDPOINTS ====================

@api_router.get("/admin/analytics")
async def get_analytics():
    """Get sales analytics for admin dashboard"""
    try:
        # Get total orders count
        total_orders = await db.orders.count_documents({})
        
        # Get orders by status
        status_counts = {}
        for status in OrderStatus:
            count = await db.orders.count_documents({"status": status.value})
            status_counts[status.value] = count
        
        # Get total revenue (only from confirmed/processing/shipped/delivered orders)
        revenue_statuses = [
            OrderStatus.PAYMENT_CONFIRMED.value,
            OrderStatus.PROCESSING.value,
            OrderStatus.SHIPPED.value,
            OrderStatus.DELIVERED.value
        ]
        
        revenue_orders = await db.orders.find(
            {"status": {"$in": revenue_statuses}},
            {"_id": 0, "total": 1}
        ).to_list(10000)
        
        total_revenue = sum(order.get("total", 0) for order in revenue_orders)
        
        # Get popular products
        all_orders = await db.orders.find({}, {"_id": 0, "items": 1}).to_list(10000)
        product_sales: Dict[str, Any] = {}
        
        for order in all_orders:
            for item in order.get("items", []):
                product_id = item.get("product_id")
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        "product_id": product_id,
                        "name": item.get("name"),
                        "total_quantity": 0,
                        "total_revenue": 0
                    }
                product_sales[product_id]["total_quantity"] += item.get("quantity", 0)
                product_sales[product_id]["total_revenue"] += item.get("price", 0) * item.get("quantity", 0)
        
        # Sort by quantity
        popular_products = sorted(
            product_sales.values(),
            key=lambda x: x["total_quantity"],
            reverse=True
        )[:10]
        
        # Get recent orders
        recent_orders = await db.orders.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        for order in recent_orders:
            order = deserialize_from_mongo(order)
        
        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "orders_by_status": status_counts,
            "popular_products": popular_products,
            "recent_orders": recent_orders
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

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