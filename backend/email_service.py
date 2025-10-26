import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import Order
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        # For now, using a simple SMTP setup
        # In production, you'd use SendGrid, AWS SES, or similar
        self.from_email = os.environ.get('SMTP_FROM_EMAIL', 'noreply@unseen.il')
        self.owner_email = os.environ.get('OWNER_EMAIL', 'unseen32.online@gmail.com')
    
    def format_order_email_html(self, order: Order, is_customer: bool = True) -> str:
        """Format order details as HTML email"""
        items_html = ""
        for item in order.items:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.product_name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.color} / {item.size}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₪{item.price * item.quantity:.2f}</td>
            </tr>
            """
        
        if is_customer:
            greeting = f"Hi {order.customer.first_name},"
            message = "Thank you for your order! We've received your order and will process it shortly."
        else:
            greeting = "New Order Received!"
            message = f"You have a new order from {order.customer.first_name} {order.customer.last_name}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Montserrat', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0A0A0A; color: #fff; padding: 20px; text-align: center; }}
                .content {{ background: #fff; padding: 30px; }}
                .order-number {{ font-size: 24px; font-weight: bold; color: #D4AF37; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f5f5f5; padding: 10px; text-align: left; font-weight: bold; }}
                .total {{ font-size: 18px; font-weight: bold; color: #D4AF37; text-align: right; padding-top: 15px; }}
                .footer {{ background: #f5f5f5; padding: 20px; text-align: center; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>UNSEEN</h1>
                    <p>International Streetwear Brand</p>
                </div>
                <div class="content">
                    <h2>{greeting}</h2>
                    <p>{message}</p>
                    <div class="order-number">Order #{order.order_number}</div>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y at %I:%M %p') if order.created_at else 'N/A'}</p>
                    
                    <h3>Order Details:</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Details</th>
                                <th style="text-align: center;">Qty</th>
                                <th style="text-align: right;">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <table style="border-top: 2px solid #0A0A0A;">
                        <tr>
                            <td colspan="3" style="text-align: right; padding: 10px;"><strong>Subtotal:</strong></td>
                            <td style="text-align: right; padding: 10px;">₪{order.subtotal:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="3" style="text-align: right; padding: 10px;"><strong>Shipping:</strong></td>
                            <td style="text-align: right; padding: 10px;">₪{order.shipping_cost:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="3" class="total">TOTAL:</td>
                            <td class="total">₪{order.total:.2f}</td>
                        </tr>
                    </table>
                    
                    <h3>Shipping Address:</h3>
                    <p>
                        {order.customer.first_name} {order.customer.last_name}<br>
                        {order.customer.address}<br>
                        {order.customer.city}, {order.customer.postal_code}<br>
                        {order.customer.country}<br>
                        <strong>Phone:</strong> {order.customer.phone}<br>
                        <strong>Email:</strong> {order.customer.email}
                    </p>
                </div>
                <div class="footer">
                    <p>UNSEEN - International Streetwear Brand</p>
                    <p>Email: unseen32.online@gmail.com | Instagram: @unseen.il</p>
                    <p>WhatsApp: +972 52-8657666</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    async def send_order_confirmation_to_customer(self, order: Order):
        """Send order confirmation email to customer"""
        subject = f"Order Confirmation #{order.order_number} - UNSEEN"
        html_content = self.format_order_email_html(order, is_customer=True)
        
        # Log email (in production, actually send it)
        print(f"\n📧 ORDER CONFIRMATION EMAIL TO CUSTOMER:")
        print(f"To: {order.customer.email}")
        print(f"Subject: {subject}")
        print(f"Order: {order.order_number}")
        print(f"Total: ₪{order.total:.2f}\n")
        
        # TODO: Implement actual email sending with SMTP or email service
        return True
    
    async def send_new_order_notification_to_owner(self, order: Order):
        """Send new order notification to store owner"""
        subject = f"🛍️ New Order #{order.order_number} - ₪{order.total:.2f}"
        html_content = self.format_order_email_html(order, is_customer=False)
        
        # Log email (in production, actually send it)
        print(f"\n📧 NEW ORDER NOTIFICATION TO OWNER:")
        print(f"To: {self.owner_email}")
        print(f"Subject: {subject}")
        print(f"Customer: {order.customer.first_name} {order.customer.last_name}")
        print(f"Total: ₪{order.total:.2f}")
        print(f"Items: {len(order.items)}\n")
        
        # TODO: Implement actual email sending
        return True
    
    async def send_shipping_notification(self, order: Order):
        """Send shipping notification to customer"""
        subject = f"Your Order #{order.order_number} Has Shipped! - UNSEEN"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Your Order Has Shipped!</h2>
            <p>Hi {order.customer.first_name},</p>
            <p>Great news! Your order <strong>#{order.order_number}</strong> has been shipped and is on its way to you.</p>
            {f'<p><strong>Tracking Number:</strong> {order.tracking_number}</p>' if order.tracking_number else ''}
            <p>Thank you for shopping with UNSEEN!</p>
        </body>
        </html>
        """
        
        print(f"\n📧 SHIPPING NOTIFICATION TO CUSTOMER:")
        print(f"To: {order.customer.email}")
        print(f"Order: {order.order_number}")
        if order.tracking_number:
            print(f"Tracking: {order.tracking_number}\n")
        
        return True
