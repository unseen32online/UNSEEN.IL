from motor.motor_asyncio import AsyncIOMotorClient
from models import Order, OrderCreate, OrderUpdate, OrderStatus
from datetime import datetime
import uuid
import os

class OrderService:
    def __init__(self, db):
        self.collection = db.orders
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order in the database"""
        order_dict = order_data.dict()
        
        # Generate unique order number
        order_number = f"UNS{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Add metadata
        order_dict['order_number'] = order_number
        order_dict['id'] = str(uuid.uuid4())
        order_dict['created_at'] = datetime.utcnow()
        order_dict['updated_at'] = datetime.utcnow()
        order_dict['status'] = OrderStatus.PENDING_PAYMENT
        order_dict['payment_status'] = 'pending'
        
        # Insert into database
        result = await self.collection.insert_one(order_dict)
        
        # Retrieve and return the created order
        created_order = await self.collection.find_one({'_id': result.inserted_id})
        created_order['id'] = created_order.pop('_id')
        
        return Order(**created_order)
    
    async def get_order_by_id(self, order_id: str) -> Order:
        """Get order by ID"""
        order = await self.collection.find_one({'id': order_id})
        if order:
            order['id'] = str(order.pop('_id', order.get('id')))
            return Order(**order)
        return None
    
    async def get_order_by_number(self, order_number: str) -> Order:
        """Get order by order number"""
        order = await self.collection.find_one({'order_number': order_number})
        if order:
            order['id'] = str(order.pop('_id', order.get('id')))
            return Order(**order)
        return None
    
    async def get_all_orders(self, skip: int = 0, limit: int = 100, status: str = None):
        """Get all orders with pagination and optional status filter"""
        query = {}
        if status:
            query['status'] = status
        
        cursor = self.collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        orders = []
        
        async for order in cursor:
            order['id'] = str(order.pop('_id', order.get('id')))
            orders.append(Order(**order))
        
        return orders
    
    async def update_order(self, order_id: str, update_data: OrderUpdate) -> Order:
        """Update order status and details"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict['updated_at'] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {'id': order_id},
            {'$set': update_dict}
        )
        
        if result.modified_count > 0:
            return await self.get_order_by_id(order_id)
        return None
    
    async def get_order_stats(self):
        """Get order statistics"""
        total_orders = await self.collection.count_documents({})
        pending_orders = await self.collection.count_documents({'status': OrderStatus.PENDING_PAYMENT})
        
        # Calculate total revenue
        pipeline = [
            {'$match': {'payment_status': 'paid'}},
            {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
        ]
        revenue_result = await self.collection.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        # Today's orders
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = await self.collection.count_documents({'created_at': {'$gte': today_start}})
        
        # Today's revenue
        today_pipeline = [
            {'$match': {'created_at': {'$gte': today_start}, 'payment_status': 'paid'}},
            {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
        ]
        today_revenue_result = await self.collection.aggregate(today_pipeline).to_list(1)
        today_revenue = today_revenue_result[0]['total'] if today_revenue_result else 0
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'today_orders': today_orders,
            'today_revenue': today_revenue
        }
