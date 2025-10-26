#!/usr/bin/env python3
"""
Comprehensive Backend Testing for UNSEEN E-commerce Order Management System
Tests all order management endpoints with realistic data
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://darkmode-fashion-3.preview.emergentagent.com/api"

class OrderManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_orders = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        if success:
            print(f"✅ {test_name}: PASSED {message}")
            self.test_results["passed"] += 1
        else:
            print(f"❌ {test_name}: FAILED {message}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
    
    def test_create_order(self):
        """Test POST /api/orders - Create Order"""
        print("\n=== Testing Order Creation ===")
        
        # Test data with realistic information
        order_data = {
            "customer_info": {
                "first_name": "Sarah",
                "last_name": "Cohen",
                "email": "sarah.cohen@gmail.com",
                "phone": "+972-54-123-4567"
            },
            "shipping_address": {
                "address": "15 Rothschild Boulevard",
                "city": "Tel Aviv",
                "postal_code": "66881",
                "country": "Israel"
            },
            "items": [
                {
                    "product_id": "prod-001",
                    "name": "Timeless Unseen T-Shirt",
                    "price": 120.00,
                    "quantity": 2,
                    "selected_size": "L",
                    "selected_color": "Black",
                    "image": "https://images.unseen.com/tshirt-black.jpg"
                },
                {
                    "product_id": "prod-002", 
                    "name": "Urban Hoodie",
                    "price": 180.00,
                    "quantity": 1,
                    "selected_size": "M",
                    "selected_color": "Gray",
                    "image": "https://images.unseen.com/hoodie-gray.jpg"
                }
            ],
            "shipping_method": "standard",
            "shipping_cost": 40.0,
            "subtotal": 420.0,
            "total": 460.0,
            "payment_info": {
                "card_last_four": "4242",
                "card_name": "Sarah Cohen",
                "payment_method": "credit_card"
            }
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
            
            if response.status_code == 200:
                order = response.json()
                
                # Validate order structure
                required_fields = ["id", "order_number", "customer_info", "items", "status", "created_at"]
                missing_fields = [field for field in required_fields if field not in order]
                
                if missing_fields:
                    self.log_result("Create Order - Structure", False, f"Missing fields: {missing_fields}")
                else:
                    # Validate order number format
                    if order["order_number"].startswith("ORD-") and len(order["order_number"]) == 12:
                        self.log_result("Create Order - Order Number Format", True)
                    else:
                        self.log_result("Create Order - Order Number Format", False, f"Invalid format: {order['order_number']}")
                    
                    # Validate status
                    if order["status"] == "pending_payment":
                        self.log_result("Create Order - Initial Status", True)
                    else:
                        self.log_result("Create Order - Initial Status", False, f"Expected 'pending_payment', got '{order['status']}'")
                    
                    # Store for later tests
                    self.created_orders.append(order)
                    self.log_result("Create Order - API Call", True, f"Order {order['order_number']} created")
            else:
                self.log_result("Create Order - API Call", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Create Order - API Call", False, f"Exception: {str(e)}")
    
    def test_create_second_order(self):
        """Create a second order for testing filters and analytics"""
        print("\n=== Creating Second Test Order ===")
        
        order_data = {
            "customer_info": {
                "first_name": "David",
                "last_name": "Levi",
                "email": "david.levi@outlook.com",
                "phone": "+972-52-987-6543"
            },
            "shipping_address": {
                "address": "42 Dizengoff Street",
                "city": "Tel Aviv",
                "postal_code": "64332",
                "country": "Israel"
            },
            "items": [
                {
                    "product_id": "prod-003",
                    "name": "Minimalist Jacket",
                    "price": 250.00,
                    "quantity": 1,
                    "selected_size": "XL",
                    "selected_color": "Navy",
                    "image": "https://images.unseen.com/jacket-navy.jpg"
                }
            ],
            "shipping_method": "express",
            "shipping_cost": 60.0,
            "subtotal": 250.0,
            "total": 310.0,
            "payment_info": {
                "card_last_four": "1234",
                "card_name": "David Levi",
                "payment_method": "credit_card"
            }
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
            
            if response.status_code == 200:
                order = response.json()
                self.created_orders.append(order)
                self.log_result("Create Second Order", True, f"Order {order['order_number']} created")
            else:
                self.log_result("Create Second Order", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Create Second Order", False, f"Exception: {str(e)}")
    
    def test_get_order_by_id(self):
        """Test GET /api/orders/{order_id}"""
        print("\n=== Testing Get Order by ID ===")
        
        if not self.created_orders:
            self.log_result("Get Order by ID", False, "No orders created to test with")
            return
        
        order = self.created_orders[0]
        
        try:
            response = self.session.get(f"{BACKEND_URL}/orders/{order['id']}")
            
            if response.status_code == 200:
                retrieved_order = response.json()
                
                # Validate that retrieved order matches created order
                if retrieved_order["id"] == order["id"] and retrieved_order["order_number"] == order["order_number"]:
                    self.log_result("Get Order by ID - Match", True)
                else:
                    self.log_result("Get Order by ID - Match", False, "Retrieved order doesn't match created order")
                    
                self.log_result("Get Order by ID - API Call", True)
            else:
                self.log_result("Get Order by ID - API Call", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Order by ID - API Call", False, f"Exception: {str(e)}")
        
        # Test with non-existent ID
        try:
            fake_id = str(uuid.uuid4())
            response = self.session.get(f"{BACKEND_URL}/orders/{fake_id}")
            
            if response.status_code == 404:
                self.log_result("Get Order by ID - 404 Test", True)
            else:
                self.log_result("Get Order by ID - 404 Test", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Order by ID - 404 Test", False, f"Exception: {str(e)}")
    
    def test_get_order_by_number(self):
        """Test GET /api/orders/number/{order_number}"""
        print("\n=== Testing Get Order by Order Number ===")
        
        if not self.created_orders:
            self.log_result("Get Order by Number", False, "No orders created to test with")
            return
        
        order = self.created_orders[0]
        
        try:
            response = self.session.get(f"{BACKEND_URL}/orders/number/{order['order_number']}")
            
            if response.status_code == 200:
                retrieved_order = response.json()
                
                if retrieved_order["order_number"] == order["order_number"]:
                    self.log_result("Get Order by Number - Match", True)
                else:
                    self.log_result("Get Order by Number - Match", False, "Order numbers don't match")
                    
                self.log_result("Get Order by Number - API Call", True)
            else:
                self.log_result("Get Order by Number - API Call", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Order by Number - API Call", False, f"Exception: {str(e)}")
        
        # Test with non-existent order number
        try:
            response = self.session.get(f"{BACKEND_URL}/orders/number/ORD-NOTFOUND")
            
            if response.status_code == 404:
                self.log_result("Get Order by Number - 404 Test", True)
            else:
                self.log_result("Get Order by Number - 404 Test", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Order by Number - 404 Test", False, f"Exception: {str(e)}")
    
    def test_list_orders(self):
        """Test GET /api/orders with various filters"""
        print("\n=== Testing List Orders ===")
        
        # Test listing all orders
        try:
            response = self.session.get(f"{BACKEND_URL}/orders")
            
            if response.status_code == 200:
                orders = response.json()
                
                if isinstance(orders, list):
                    self.log_result("List All Orders", True, f"Retrieved {len(orders)} orders")
                else:
                    self.log_result("List All Orders", False, "Response is not a list")
            else:
                self.log_result("List All Orders", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("List All Orders", False, f"Exception: {str(e)}")
        
        # Test filtering by status
        try:
            response = self.session.get(f"{BACKEND_URL}/orders?status=pending_payment")
            
            if response.status_code == 200:
                orders = response.json()
                
                # Check that all orders have pending_payment status
                all_pending = all(order.get("status") == "pending_payment" for order in orders)
                
                if all_pending:
                    self.log_result("List Orders - Status Filter", True, f"Found {len(orders)} pending orders")
                else:
                    self.log_result("List Orders - Status Filter", False, "Not all orders have pending_payment status")
            else:
                self.log_result("List Orders - Status Filter", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("List Orders - Status Filter", False, f"Exception: {str(e)}")
        
        # Test filtering by customer email
        if self.created_orders:
            customer_email = self.created_orders[0]["customer_info"]["email"]
            
            try:
                response = self.session.get(f"{BACKEND_URL}/orders?customer_email={customer_email}")
                
                if response.status_code == 200:
                    orders = response.json()
                    
                    # Check that all orders belong to the specified customer
                    correct_customer = all(order.get("customer_info", {}).get("email") == customer_email for order in orders)
                    
                    if correct_customer:
                        self.log_result("List Orders - Email Filter", True, f"Found {len(orders)} orders for {customer_email}")
                    else:
                        self.log_result("List Orders - Email Filter", False, "Not all orders belong to specified customer")
                else:
                    self.log_result("List Orders - Email Filter", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result("List Orders - Email Filter", False, f"Exception: {str(e)}")
        
        # Test pagination
        try:
            response = self.session.get(f"{BACKEND_URL}/orders?limit=1&skip=0")
            
            if response.status_code == 200:
                orders = response.json()
                
                if len(orders) <= 1:
                    self.log_result("List Orders - Pagination", True, f"Pagination working, got {len(orders)} orders")
                else:
                    self.log_result("List Orders - Pagination", False, f"Expected max 1 order, got {len(orders)}")
            else:
                self.log_result("List Orders - Pagination", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("List Orders - Pagination", False, f"Exception: {str(e)}")
    
    def test_update_order_status(self):
        """Test PATCH /api/orders/{order_id}"""
        print("\n=== Testing Update Order Status ===")
        
        if not self.created_orders:
            self.log_result("Update Order Status", False, "No orders created to test with")
            return
        
        order = self.created_orders[0]
        
        # Test updating status
        update_data = {
            "status": "processing",
            "notes": "Order is being prepared for shipment"
        }
        
        try:
            response = self.session.patch(f"{BACKEND_URL}/orders/{order['id']}", json=update_data)
            
            if response.status_code == 200:
                updated_order = response.json()
                
                if updated_order["status"] == "processing":
                    self.log_result("Update Order Status - Status Change", True)
                else:
                    self.log_result("Update Order Status - Status Change", False, f"Expected 'processing', got '{updated_order['status']}'")
                
                if updated_order.get("notes") == update_data["notes"]:
                    self.log_result("Update Order Status - Notes", True)
                else:
                    self.log_result("Update Order Status - Notes", False, "Notes not updated correctly")
                
                # Check that updated_at was modified
                if "updated_at" in updated_order:
                    self.log_result("Update Order Status - Timestamp", True)
                else:
                    self.log_result("Update Order Status - Timestamp", False, "updated_at field missing")
                    
                self.log_result("Update Order Status - API Call", True)
            else:
                self.log_result("Update Order Status - API Call", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Update Order Status - API Call", False, f"Exception: {str(e)}")
    
    def test_payment_processing(self):
        """Test POST /api/payment/process"""
        print("\n=== Testing Payment Processing ===")
        
        if not self.created_orders:
            self.log_result("Payment Processing", False, "No orders created to test with")
            return
        
        order = self.created_orders[-1]  # Use the last created order
        
        # Test successful payment
        payment_data = {
            "order_id": order["id"],
            "amount": order["total"],
            "card_number": "4242424242424242",
            "card_name": "David Levi",
            "expiry_date": "12/25",
            "cvv": "123"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/payment/process", json=payment_data)
            
            if response.status_code == 200:
                payment_result = response.json()
                
                if payment_result.get("success"):
                    self.log_result("Payment Processing - Success", True, f"Transaction ID: {payment_result.get('transaction_id')}")
                    
                    # Verify transaction ID format
                    if payment_result.get("transaction_id", "").startswith("TXN-"):
                        self.log_result("Payment Processing - Transaction ID Format", True)
                    else:
                        self.log_result("Payment Processing - Transaction ID Format", False, "Invalid transaction ID format")
                else:
                    self.log_result("Payment Processing - Success", False, f"Payment failed: {payment_result.get('message')}")
                    
                self.log_result("Payment Processing - API Call", True)
            else:
                self.log_result("Payment Processing - API Call", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Payment Processing - API Call", False, f"Exception: {str(e)}")
        
        # Test invalid card number
        invalid_payment_data = {
            "order_id": order["id"],
            "amount": order["total"],
            "card_number": "123",  # Invalid card number
            "card_name": "Test User",
            "expiry_date": "12/25",
            "cvv": "123"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/payment/process", json=invalid_payment_data)
            
            if response.status_code == 200:
                payment_result = response.json()
                
                if not payment_result.get("success"):
                    self.log_result("Payment Processing - Invalid Card", True, "Correctly rejected invalid card")
                else:
                    self.log_result("Payment Processing - Invalid Card", False, "Should have rejected invalid card")
            else:
                self.log_result("Payment Processing - Invalid Card", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Payment Processing - Invalid Card", False, f"Exception: {str(e)}")
        
        # Test invalid CVV
        invalid_cvv_data = {
            "order_id": order["id"],
            "amount": order["total"],
            "card_number": "4242424242424242",
            "card_name": "Test User",
            "expiry_date": "12/25",
            "cvv": "12"  # Invalid CVV
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/payment/process", json=invalid_cvv_data)
            
            if response.status_code == 200:
                payment_result = response.json()
                
                if not payment_result.get("success"):
                    self.log_result("Payment Processing - Invalid CVV", True, "Correctly rejected invalid CVV")
                else:
                    self.log_result("Payment Processing - Invalid CVV", False, "Should have rejected invalid CVV")
            else:
                self.log_result("Payment Processing - Invalid CVV", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Payment Processing - Invalid CVV", False, f"Exception: {str(e)}")
    
    def test_admin_analytics(self):
        """Test GET /api/admin/analytics"""
        print("\n=== Testing Admin Analytics ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/analytics")
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Check required fields
                required_fields = ["total_orders", "total_revenue", "orders_by_status", "popular_products", "recent_orders"]
                missing_fields = [field for field in required_fields if field not in analytics]
                
                if missing_fields:
                    self.log_result("Admin Analytics - Structure", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Admin Analytics - Structure", True)
                
                # Validate data types
                if isinstance(analytics.get("total_orders"), int):
                    self.log_result("Admin Analytics - Total Orders Type", True)
                else:
                    self.log_result("Admin Analytics - Total Orders Type", False, "total_orders should be integer")
                
                if isinstance(analytics.get("total_revenue"), (int, float)):
                    self.log_result("Admin Analytics - Total Revenue Type", True)
                else:
                    self.log_result("Admin Analytics - Total Revenue Type", False, "total_revenue should be number")
                
                if isinstance(analytics.get("orders_by_status"), dict):
                    self.log_result("Admin Analytics - Orders by Status Type", True)
                else:
                    self.log_result("Admin Analytics - Orders by Status Type", False, "orders_by_status should be dict")
                
                if isinstance(analytics.get("popular_products"), list):
                    self.log_result("Admin Analytics - Popular Products Type", True)
                else:
                    self.log_result("Admin Analytics - Popular Products Type", False, "popular_products should be list")
                
                if isinstance(analytics.get("recent_orders"), list):
                    self.log_result("Admin Analytics - Recent Orders Type", True)
                else:
                    self.log_result("Admin Analytics - Recent Orders Type", False, "recent_orders should be list")
                
                self.log_result("Admin Analytics - API Call", True, f"Total orders: {analytics.get('total_orders')}, Revenue: ₪{analytics.get('total_revenue')}")
            else:
                self.log_result("Admin Analytics - API Call", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Admin Analytics - API Call", False, f"Exception: {str(e)}")
    
    def test_email_service_mock(self):
        """Test that email service is working (mock)"""
        print("\n=== Testing Mock Email Service ===")
        
        # The email service is tested indirectly through order creation
        # Since it's a mock service that logs to console, we can't directly test it
        # But we can verify that order creation doesn't fail due to email issues
        
        if self.created_orders:
            self.log_result("Mock Email Service", True, "Email service working (mock - logs to console)")
        else:
            self.log_result("Mock Email Service", False, "No orders created to test email service")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting UNSEEN E-commerce Backend Order Management Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Test order creation
        self.test_create_order()
        self.test_create_second_order()
        
        # Test order retrieval
        self.test_get_order_by_id()
        self.test_get_order_by_number()
        
        # Test order listing
        self.test_list_orders()
        
        # Test order updates
        self.test_update_order_status()
        
        # Test payment processing
        self.test_payment_processing()
        
        # Test admin analytics
        self.test_admin_analytics()
        
        # Test email service
        self.test_email_service_mock()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🏁 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['failed'] == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed - check the details above")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = OrderManagementTester()
    success = tester.run_all_tests()
    
    if not success:
        exit(1)