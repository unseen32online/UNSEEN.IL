import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { CheckCircle, Package, MapPin, CreditCard, Mail, Phone } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const OrderConfirmation = () => {
  const { orderNumber } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/orders/number/${orderNumber}`);
        setOrder(response.data);
      } catch (err) {
        console.error('Error fetching order:', err);
        setError('Order not found');
      } finally {
        setLoading(false);
      }
    };

    if (orderNumber) {
      fetchOrder();
    }
  }, [orderNumber]);

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center py-16">
            <div className="animate-pulse">
              <div className="h-8 bg-dark-tertiary rounded w-1/2 mx-auto mb-4"></div>
              <div className="h-4 bg-dark-tertiary rounded w-1/3 mx-auto"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center py-16">
            <Package className="w-16 h-16 mx-auto text-warm-gray mb-4" />
            <h2 className="text-2xl font-light mb-4">Order Not Found</h2>
            <p className="text-warm-gray mb-8">We couldn't find the order you're looking for.</p>
            <Button className="primary-button" onClick={() => navigate('/')}>
              Back to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      pending_payment: 'text-yellow-500',
      payment_confirmed: 'text-green-500',
      processing: 'text-blue-500',
      shipped: 'text-purple-500',
      delivered: 'text-green-600',
      cancelled: 'text-red-500'
    };
    return colors[status] || 'text-accent-gray';
  };

  const getStatusText = (status) => {
    const texts = {
      pending_payment: 'Pending Payment',
      payment_confirmed: 'Payment Confirmed',
      processing: 'Processing',
      shipped: 'Shipped',
      delivered: 'Delivered',
      cancelled: 'Cancelled'
    };
    return texts[status] || status;
  };

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-4xl mx-auto px-6">
        {/* Success Header */}
        <div className="text-center mb-12">
          <CheckCircle className="w-20 h-20 mx-auto text-green-500 mb-6" />
          <h1 className="page-title mb-4">Order Confirmed!</h1>
          <p className="text-lg text-accent-gray mb-2">
            Thank you for your order, {order.customer_info.first_name}!
          </p>
          <p className="text-accent-gray">
            A confirmation email has been sent to {order.customer_info.email}
          </p>
        </div>

        {/* Order Number */}
        <div className="bg-dark-secondary border border-dark p-6 mb-8">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-accent-gray mb-1">Order Number</p>
              <p className="text-2xl font-bold text-accent-gold">{order.order_number}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-accent-gray mb-1">Status</p>
              <p className={`text-lg font-bold ${getStatusColor(order.status)}`}>
                {getStatusText(order.status)}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Customer Information */}
          <div className="checkout-section">
            <div className="flex items-center mb-4">
              <Mail className="w-5 h-5 mr-3 text-accent-gold" />
              <h2 className="text-xl font-bold text-accent-primary">Contact Information</h2>
            </div>
            <div className="space-y-2 text-accent-gray">
              <p className="flex items-center">
                <Mail className="w-4 h-4 mr-2" />
                {order.customer_info.email}
              </p>
              <p className="flex items-center">
                <Phone className="w-4 h-4 mr-2" />
                {order.customer_info.phone}
              </p>
            </div>
          </div>

          {/* Shipping Address */}
          <div className="checkout-section">
            <div className="flex items-center mb-4">
              <MapPin className="w-5 h-5 mr-3 text-accent-gold" />
              <h2 className="text-xl font-bold text-accent-primary">Shipping Address</h2>
            </div>
            <div className="text-accent-gray">
              <p>{order.shipping_address.address}</p>
              <p>{order.shipping_address.city}, {order.shipping_address.postal_code}</p>
              <p>{order.shipping_address.country}</p>
            </div>
          </div>
        </div>

        {/* Order Items */}
        <div className="checkout-section mb-8">
          <div className="flex items-center mb-6">
            <Package className="w-5 h-5 mr-3 text-accent-gold" />
            <h2 className="text-xl font-bold text-accent-primary">Order Items</h2>
          </div>
          <div className="space-y-4">
            {order.items.map((item, index) => (
              <div key={index} className="flex gap-4 pb-4 border-b border-dark last:border-0">
                <div className="w-20 h-20 bg-dark-tertiary border border-dark flex items-center justify-center">
                  {item.image ? (
                    <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="text-xs text-accent-gray">IMG</div>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-accent-primary mb-1">{item.name}</h3>
                  <p className="text-sm text-accent-gray">
                    Color: {item.selected_color} | Size: {item.selected_size}
                  </p>
                  <p className="text-sm text-accent-gray">Quantity: {item.quantity}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-accent-gold">₪{(item.price * item.quantity).toFixed(2)}</p>
                  <p className="text-sm text-accent-gray">₪{item.price.toFixed(2)} each</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary */}
        <div className="checkout-section mb-8">
          <div className="flex items-center mb-6">
            <CreditCard className="w-5 h-5 mr-3 text-accent-gold" />
            <h2 className="text-xl font-bold text-accent-primary">Order Summary</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between text-accent-gray">
              <span>Subtotal</span>
              <span>₪{order.subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-accent-gray">
              <span>Shipping ({order.shipping_method})</span>
              <span>₪{order.shipping_cost.toFixed(2)}</span>
            </div>
            <div className="border-t border-dark pt-3 flex justify-between">
              <span className="text-xl font-bold text-accent-primary">Total</span>
              <span className="text-xl font-bold text-accent-gold">₪{order.total.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-center gap-4">
          <Button className="primary-button" onClick={() => navigate('/')}>
            Continue Shopping
          </Button>
          <Button 
            variant="outline" 
            className="border-accent-gold text-accent-gold hover:bg-accent-gold hover:text-dark-bg"
            onClick={() => window.print()}
          >
            Print Order
          </Button>
        </div>

        {/* Additional Info */}
        <div className="mt-12 text-center text-accent-gray text-sm">
          <p className="mb-2">Questions about your order?</p>
          <p>
            Email us at{' '}
            <a href="mailto:unseen.info9@gmail.com" className="text-accent-gold hover:underline">
              unseen.info9@gmail.com
            </a>
            {' '}or contact us on{' '}
            <a href="https://wa.me/972546803020" className="text-accent-gold hover:underline">
              WhatsApp
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;
