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
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL')
SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME')

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

# ==================== AUTHENTICATION UTILITIES ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return admin user"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Verify admin exists in database
        admin = await db.admins.find_one({"username": username}, {"_id": 0})
        if admin is None:
            raise credentials_exception
        
        return admin
    except JWTError:
        raise credentials_exception



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

# Discount Code Models
class DiscountCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    discount_type: str  # "percentage" or "fixed"
    discount_value: float  # percentage (0-100) or fixed amount
    min_order_amount: float = 0
    max_uses: Optional[int] = None
    current_uses: int = 0
    active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DiscountCodeCreate(BaseModel):
    code: str
    discount_type: str  # "percentage" or "fixed"
    discount_value: float
    min_order_amount: float = 0
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None

class DiscountCodeValidation(BaseModel):
    code: str
    order_total: float

class DiscountCodeResponse(BaseModel):
    valid: bool
    discount_amount: float = 0
    message: str
    code: Optional[str] = None

# Admin Models
class AdminUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

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
    discount_code: Optional[str] = None
    discount_amount: float = 0

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
    discount_code: Optional[str] = None
    discount_amount: float = 0
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

# ==================== ADMIN AUTHENTICATION ENDPOINTS ====================

@api_router.post("/admin/setup", response_model=dict)
async def setup_admin(admin_data: AdminLogin):
    """Create initial admin user (only if no admins exist)"""
    existing_admin = await db.admins.find_one({})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists. Use login endpoint.")
    
    # Create admin user
    admin = AdminUser(
        username=admin_data.username,
        password_hash=get_password_hash(admin_data.password)
    )
    
    admin_dict = admin.model_dump()
    admin_dict['created_at'] = admin_dict['created_at'].isoformat()
    
    await db.admins.insert_one(admin_dict)
    
    logger.info(f"Admin user created: {admin_data.username}")
    return {"message": "Admin user created successfully", "username": admin_data.username}

@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint"""
    # Find admin user
    admin = await db.admins.find_one({"username": login_data.username}, {"_id": 0})
    
    if not admin or not verify_password(login_data.password, admin['password_hash']):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": admin['username']})
    
    logger.info(f"Admin logged in: {admin['username']}")
    return AdminLoginResponse(
        access_token=access_token,
        username=admin['username']
    )

@api_router.get("/admin/verify")
async def verify_admin(admin: dict = Depends(get_current_admin)):
    """Verify admin token"""
    return {"username": admin['username'], "valid": True}

# ==================== DISCOUNT CODE ENDPOINTS ====================

@api_router.post("/discount/validate", response_model=DiscountCodeResponse)
async def validate_discount_code(validation: DiscountCodeValidation):
    """Validate a discount code"""
    try:
        # Find discount code
        code = await db.discount_codes.find_one(
            {"code": validation.code.upper(), "active": True},
            {"_id": 0}
        )
        
        if not code:
            return DiscountCodeResponse(
                valid=False,
                message="Invalid discount code"
            )
        
        # Check if expired
        if code.get('expires_at'):
            expires_at = datetime.fromisoformat(code['expires_at']) if isinstance(code['expires_at'], str) else code['expires_at']
            if expires_at < datetime.now(timezone.utc):
                return DiscountCodeResponse(
                    valid=False,
                    message="This discount code has expired"
                )
        
        # Check max uses
        if code.get('max_uses') and code.get('current_uses', 0) >= code['max_uses']:
            return DiscountCodeResponse(
                valid=False,
                message="This discount code has reached its usage limit"
            )
        
        # Check minimum order amount
        if validation.order_total < code.get('min_order_amount', 0):
            return DiscountCodeResponse(
                valid=False,
                message=f"Minimum order amount of ₪{code['min_order_amount']:.2f} required"
            )
        
        # Calculate discount
        discount_amount = 0
        if code['discount_type'] == 'percentage':
            discount_amount = (validation.order_total * code['discount_value']) / 100
        else:  # fixed
            discount_amount = code['discount_value']
        
        # Ensure discount doesn't exceed order total
        discount_amount = min(discount_amount, validation.order_total)
        
        return DiscountCodeResponse(
            valid=True,
            discount_amount=round(discount_amount, 2),
            message=f"Discount applied: ₪{discount_amount:.2f} off!",
            code=code['code']
        )
    except Exception as e:
        logger.error(f"Error validating discount code: {str(e)}")
        return DiscountCodeResponse(
            valid=False,
            message="Error validating discount code"
        )

@api_router.post("/admin/discount-codes", response_model=dict)
async def create_discount_code(code_data: DiscountCodeCreate, admin: dict = Depends(get_current_admin)):
    """Create a new discount code (admin only)"""
    try:
        # Check if code already exists
        existing = await db.discount_codes.find_one({"code": code_data.code.upper()}, {"_id": 0})
        if existing:
            raise HTTPException(status_code=400, detail="Discount code already exists")
        
        # Create discount code
        discount_code = DiscountCode(
            code=code_data.code.upper(),
            discount_type=code_data.discount_type,
            discount_value=code_data.discount_value,
            min_order_amount=code_data.min_order_amount,
            max_uses=code_data.max_uses,
            expires_at=code_data.expires_at
        )
        
        code_dict = discount_code.model_dump()
        code_dict = serialize_for_mongo(code_dict)
        
        await db.discount_codes.insert_one(code_dict)
        
        logger.info(f"Discount code created by {admin['username']}: {code_data.code}")
        return {"message": "Discount code created successfully", "code": code_data.code.upper()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating discount code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create discount code")

@api_router.get("/admin/discount-codes", response_model=List[dict])
async def list_discount_codes(admin: dict = Depends(get_current_admin)):
    """List all discount codes (admin only)"""
    codes = await db.discount_codes.find({}, {"_id": 0}).to_list(1000)
    for code in codes:
        code = deserialize_from_mongo(code)
    return codes

@api_router.delete("/admin/discount-codes/{code}")
async def delete_discount_code(code: str, admin: dict = Depends(get_current_admin)):
    """Delete a discount code (admin only)"""
    result = await db.discount_codes.delete_one({"code": code.upper()})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    logger.info(f"Discount code deleted by {admin['username']}: {code}")
    return {"message": "Discount code deleted successfully"}

@api_router.post("/admin/discount-codes/create-sample")
async def create_sample_discount_codes(admin: dict = Depends(get_current_admin)):
    """Create sample discount codes for testing"""
    sample_codes = [
        {
            "code": "WELCOME10",
            "discount_type": "percentage",
            "discount_value": 10,
            "min_order_amount": 100,
            "max_uses": 100,
            "expires_at": None
        },
        {
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20,
            "min_order_amount": 200,
            "max_uses": 50,
            "expires_at": None
        },
        {
            "code": "FREESHIP",
            "discount_type": "fixed",
            "discount_value": 40,
            "min_order_amount": 150,
            "max_uses": None,
            "expires_at": None
        }
    ]
    
    created = []
    for code_data in sample_codes:
        existing = await db.discount_codes.find_one({"code": code_data["code"]}, {"_id": 0})
        if not existing:
            discount_code = DiscountCode(**code_data, active=True)
            code_dict = discount_code.model_dump()
            code_dict = serialize_for_mongo(code_dict)
            await db.discount_codes.insert_one(code_dict)
            created.append(code_data["code"])
    
    return {"message": "Sample discount codes created", "codes": created}

@api_router.get("/admin/verify")
async def verify_admin(admin: dict = Depends(get_current_admin)):
    """Verify admin token"""
    return {"username": admin['username'], "valid": True}

@api_router.post("/admin/create", response_model=dict)
async def create_admin(admin_data: AdminLogin, current_admin: dict = Depends(get_current_admin)):
    """Create a new admin user (requires existing admin authentication)"""
    # Check if username already exists
    existing_admin = await db.admins.find_one({"username": admin_data.username}, {"_id": 0})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new admin user
    new_admin = AdminUser(
        username=admin_data.username,
        password_hash=get_password_hash(admin_data.password)
    )
    
    admin_dict = new_admin.model_dump()
    admin_dict['created_at'] = admin_dict['created_at'].isoformat()
    
    await db.admins.insert_one(admin_dict)
    
    logger.info(f"New admin user created by {current_admin['username']}: {admin_data.username}")
    return {"message": "Admin user created successfully", "username": admin_data.username}

@api_router.post("/admin/change-password", response_model=dict)
async def change_password(password_data: dict, current_admin: dict = Depends(get_current_admin)):
    """Change current admin password"""
    new_password = password_data.get('new_password')
    
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Update password
    new_hash = get_password_hash(new_password)
    await db.admins.update_one(
        {"username": current_admin['username']},
        {"$set": {"password_hash": new_hash}}
    )
    
    logger.info(f"Admin password changed: {current_admin['username']}")
    return {"message": "Password changed successfully"}

@api_router.delete("/admin/delete/{username}")
async def delete_admin(username: str, current_admin: dict = Depends(get_current_admin)):
    """Delete an admin user (cannot delete yourself)"""
    if username == current_admin['username']:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await db.admins.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    logger.info(f"Admin user deleted by {current_admin['username']}: {username}")
    return {"message": "Admin user deleted successfully", "username": username}

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

# SendGrid Email Service
async def send_order_confirmation_email(order: Order):
    """Send order confirmation email via SendGrid"""
    try:
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0A0A0A; color: #FFFFFF; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 32px; letter-spacing: 2px; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .order-details {{ background-color: #ffffff; padding: 20px; margin: 20px 0; border-left: 4px solid #D4AF37; }}
                .item {{ padding: 15px; border-bottom: 1px solid #eee; }}
                .item:last-child {{ border-bottom: none; }}
                .total {{ font-size: 20px; font-weight: bold; color: #D4AF37; padding: 20px; background-color: #ffffff; text-align: right; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .status {{ display: inline-block; padding: 5px 15px; background-color: #D4AF37; color: #0A0A0A; font-weight: bold; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>UNSEEN IL</h1>
                </div>
                
                <div class="content">
                    <h2>Order Confirmation</h2>
                    <p>Dear {order.customer_info.first_name} {order.customer_info.last_name},</p>
                    <p>Thank you for your order! We're excited to get your items to you.</p>
                    
                    <div class="order-details">
                        <p><strong>Order Number:</strong> {order.order_number}</p>
                        <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y at %H:%M')}</p>
                        <p><strong>Status:</strong> <span class="status">{order.status.value.replace('_', ' ').title()}</span></p>
                    </div>
                    
                    <h3>Order Items:</h3>
                    <div class="order-details">
        """
        
        for item in order.items:
            html_content += f"""
                        <div class="item">
                            <strong>{item.name}</strong><br>
                            Color: {item.selected_color} | Size: {item.selected_size}<br>
                            Quantity: {item.quantity} × ₪{item.price:.2f} = ₪{(item.price * item.quantity):.2f}
                        </div>
        """
        
        html_content += f"""
                    </div>
                    
                    <div class="order-details">
                        <p><strong>Subtotal:</strong> ₪{order.subtotal:.2f}</p>
        """
        
        if order.discount_amount > 0:
            html_content += f"""
                        <p><strong>Discount ({order.discount_code}):</strong> <span style="color: #D4AF37;">-₪{order.discount_amount:.2f}</span></p>
        """
        
        html_content += f"""
                        <p><strong>Shipping ({order.shipping_method}):</strong> ₪{order.shipping_cost:.2f}</p>
                        <div class="total">Total: ₪{order.total:.2f}</div>
                    </div>
                    
                    <h3>Shipping Address:</h3>
                    <div class="order-details">
                        <p>
                            {order.shipping_address.address}<br>
                            {order.shipping_address.city}, {order.shipping_address.postal_code}<br>
                            {order.shipping_address.country}
                        </p>
                    </div>
                    
                    <p>We will notify you when your order ships.</p>
                    <p>If you have any questions, please contact us at {SENDGRID_FROM_EMAIL}</p>
                </div>
                
                <div class="footer">
                    <p>Thank you for shopping with UNSEEN IL</p>
                    <p>&copy; 2024 UNSEEN IL. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Order Confirmation - UNSEEN IL
        
        Dear {order.customer_info.first_name} {order.customer_info.last_name},
        
        Thank you for your order!
        
        Order Number: {order.order_number}
        Order Date: {order.created_at.strftime('%B %d, %Y at %H:%M')}
        Status: {order.status.value.replace('_', ' ').title()}
        
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
        
        Thank you for shopping with UNSEEN IL!
        """
        
        # Create SendGrid message
        message = Mail(
            from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
            to_emails=To(order.customer_info.email),
            subject=f'Order Confirmation - {order.order_number}',
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Send email
        if SENDGRID_API_KEY:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Order confirmation email sent to {order.customer_info.email} - Status: {response.status_code}")
            return True
        else:
            logger.warning("SendGrid API key not configured. Email not sent.")
            return False
            
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {str(e)}")
        # Log more details for debugging
        if hasattr(e, 'body'):
            logger.error(f"SendGrid error details: {e.body}")
        return False

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
async def get_analytics(admin: dict = Depends(get_current_admin)):
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