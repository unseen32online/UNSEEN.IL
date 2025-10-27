"""
HYP Payment Gateway Client
Handles XML-based communication with HYP/Yaad Sarig payment system
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid
from typing import Dict, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class HYPPaymentClient:
    """Client for HYP/Yaad Sarig payment gateway"""
    
    def __init__(self):
        self.merchant_name = os.getenv('HYP_MERCHANT_NAME')
        self.terminal_id = os.getenv('HYP_TERMINAL_ID')
        self.user_id = os.getenv('HYP_USER_ID')
        self.api_password = os.getenv('HYP_API_PASSWORD')
        self.api_endpoint = os.getenv('HYP_API_ENDPOINT', 'http://icom.yaad.net/')
        self.environment = os.getenv('HYP_ENVIRONMENT', 'production')
        
        # Ensure endpoint ends with /
        if not self.api_endpoint.endswith('/'):
            self.api_endpoint += '/'
        
        logger.info(f"HYP Client initialized (Environment: {self.environment}, Terminal: {self.terminal_id})")
    
    def _generate_unique_id(self) -> str:
        """Generate unique transaction ID"""
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
    
    def _build_payment_request_xml(self,
                                   amount: float,
                                   card_number: str,
                                   expiry_month: str,
                                   expiry_year: str,
                                   cvv: str,
                                   order_id: str,
                                   customer_name: str = "",
                                   currency: str = "1") -> str:
        """
        Build XML request for HYP payment processing
        
        Args:
            amount: Amount in ILS (will be converted to agorot internally)
            card_number: Credit card number
            expiry_month: MM format
            expiry_year: YY format
            cvv: Card CVV
            order_id: Unique order identifier
            customer_name: Customer name
            currency: Currency code (1 = ILS)
        """
        # Convert amount to agorot (cents)
        amount_agorot = int(amount * 100)
        
        # Build XML
        root = ET.Element('ashrait')
        request = ET.SubElement(root, 'request')
        
        # Authentication
        ET.SubElement(request, 'username').text = self.user_id
        ET.SubElement(request, 'password').text = self.api_password
        
        # Transaction details
        ET.SubElement(request, 'command').text = 'doDeal'
        ET.SubElement(request, 'Masof').text = self.terminal_id
        ET.SubElement(request, 'action').text = 'J5'  # Sale transaction
        ET.SubElement(request, 'sum').text = str(amount_agorot)
        ET.SubElement(request, 'currency').text = currency
        
        # Card details
        ET.SubElement(request, 'cardNumber').text = card_number
        ET.SubElement(request, 'cardExpiration').text = f"{expiry_month}{expiry_year}"
        ET.SubElement(request, 'CVV2').text = cvv
        
        # Additional info
        ET.SubElement(request, 'id').text = order_id
        ET.SubElement(request, 'comments').text = f"Order: {order_id}"
        
        if customer_name:
            ET.SubElement(request, 'info').text = customer_name
        
        # Convert to string
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        
        return xml_string
    
    def _parse_response(self, xml_response: str) -> Dict[str, Any]:
        """Parse XML response from HYP"""
        try:
            root = ET.fromstring(xml_response)
            
            response_dict = {}
            
            # Parse all response elements
            for child in root:
                response_dict[child.tag] = child.text
            
            return response_dict
        
        except ET.ParseError as e:
            logger.error(f"Failed to parse HYP response: {str(e)}")
            logger.error(f"Response was: {xml_response[:500]}")
            return {
                'error': 'parse_error',
                'message': f"Failed to parse response: {str(e)}"
            }
    
    def process_payment(self,
                       amount: float,
                       card_number: str,
                       expiry_month: str,
                       expiry_year: str,
                       cvv: str,
                       order_id: str,
                       customer_name: str = "") -> Dict[str, Any]:
        """
        Process a payment through HYP
        
        Args:
            amount: Amount in ILS
            card_number: Credit card number
            expiry_month: Month (MM)
            expiry_year: Year (YY)
            cvv: Card CVV
            order_id: Unique order ID
            customer_name: Customer name
        
        Returns:
            Dictionary with payment result
        """
        try:
            # Build XML request
            xml_payload = self._build_payment_request_xml(
                amount=amount,
                card_number=card_number,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                cvv=cvv,
                order_id=order_id,
                customer_name=customer_name
            )
            
            # Mask sensitive data for logging
            masked_card = f"****{card_number[-4:]}" if len(card_number) >= 4 else "****"
            logger.info(f"Processing HYP payment for order {order_id}, amount: ₪{amount:.2f}, card: {masked_card}")
            
            # Send request to HYP
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            # HYP expects data as form parameter 'data'
            response = requests.post(
                self.api_endpoint,
                data={'data': xml_payload},
                headers=headers,
                timeout=30
            )
            
            logger.info(f"HYP response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"HYP returned HTTP {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP error: {response.status_code}",
                    'order_id': order_id
                }
            
            # Parse response
            result = self._parse_response(response.text)
            
            # Check if transaction was successful
            # HYP returns 'responsecode' where '00' or '0' = success
            response_code = result.get('responsecode', result.get('ResponseCode', ''))
            is_success = response_code in ['0', '00']
            
            # Extract transaction details
            transaction_id = result.get('transactionid', result.get('TransactionID', ''))
            auth_number = result.get('approvalcode', result.get('ApprovalCode', ''))
            response_message = result.get('responsemessage', result.get('ResponseMessage', 'Unknown error'))
            
            if is_success:
                logger.info(f"✅ Payment successful for order {order_id}, Transaction ID: {transaction_id}")
            else:
                logger.warning(f"❌ Payment failed for order {order_id}, Code: {response_code}, Message: {response_message}")
            
            return {
                'success': is_success,
                'transaction_id': transaction_id,
                'authorization_code': auth_number,
                'response_code': response_code,
                'response_message': response_message,
                'order_id': order_id,
                'amount': amount,
                'raw_response': result
            }
        
        except requests.Timeout:
            logger.error(f"HYP request timeout for order {order_id}")
            return {
                'success': False,
                'error': 'timeout',
                'message': 'Payment gateway timeout',
                'order_id': order_id
            }
        
        except requests.RequestException as e:
            logger.error(f"Network error with HYP: {str(e)}")
            return {
                'success': False,
                'error': 'network_error',
                'message': f"Network error: {str(e)}",
                'order_id': order_id
            }
        
        except Exception as e:
            logger.error(f"Unexpected error processing payment: {str(e)}")
            return {
                'success': False,
                'error': 'unexpected_error',
                'message': str(e),
                'order_id': order_id
            }
    
    def refund_payment(self,
                      original_transaction_id: str,
                      amount: float,
                      order_id: str) -> Dict[str, Any]:
        """
        Process a refund for a previous transaction
        
        Args:
            original_transaction_id: Original HYP transaction ID
            amount: Refund amount in ILS
            order_id: Associated order ID
        """
        try:
            amount_agorot = int(amount * 100)
            
            # Build refund XML
            root = ET.Element('ashrait')
            request = ET.SubElement(root, 'request')
            
            ET.SubElement(request, 'username').text = self.user_id
            ET.SubElement(request, 'password').text = self.api_password
            ET.SubElement(request, 'command').text = 'doDeal'
            ET.SubElement(request, 'Masof').text = self.terminal_id
            ET.SubElement(request, 'action').text = 'J6'  # Refund transaction
            ET.SubElement(request, 'sum').text = str(amount_agorot)
            ET.SubElement(request, 'transactionId').text = original_transaction_id
            ET.SubElement(request, 'id').text = order_id
            
            xml_payload = ET.tostring(root, encoding='unicode', method='xml')
            
            logger.info(f"Processing refund for order {order_id}, amount: ₪{amount:.2f}")
            
            response = requests.post(
                self.api_endpoint,
                data={'data': xml_payload},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            result = self._parse_response(response.text)
            response_code = result.get('responsecode', result.get('ResponseCode', ''))
            is_success = response_code in ['0', '00']
            
            if is_success:
                logger.info(f"✅ Refund successful for order {order_id}")
            else:
                logger.warning(f"❌ Refund failed for order {order_id}")
            
            return {
                'success': is_success,
                'refund_transaction_id': result.get('transactionid', ''),
                'response_code': response_code,
                'response_message': result.get('responsemessage', ''),
                'order_id': order_id,
                'amount': amount,
                'raw_response': result
            }
        
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'order_id': order_id
            }

# Global instance
hyp_client = HYPPaymentClient()
