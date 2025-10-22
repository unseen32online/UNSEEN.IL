import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { Button } from '../components/ui/button';
import { useToast } from '../hooks/use-toast';
import { CreditCard, Package, MapPin, User } from 'lucide-react';

const Checkout = () => {
  const navigate = useNavigate();
  const { cartItems, cartTotal, clearCart } = useCart();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    // Personal Information
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    
    // Shipping Address
    address: '',
    city: '',
    postalCode: '',
    country: 'Israel',
    
    // Payment Information
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: ''
  });

  const [shippingMethod, setShippingMethod] = useState('standard');

  const shippingCost = shippingMethod === 'express' ? 60 : 40;
  const finalTotal = cartTotal + shippingCost;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.phone) {
      toast({
        title: "Missing Information",
        description: "Please fill in all personal information fields",
        variant: "destructive"
      });
      return;
    }

    if (!formData.address || !formData.city || !formData.postalCode) {
      toast({
        title: "Missing Address",
        description: "Please fill in all shipping address fields",
        variant: "destructive"
      });
      return;
    }

    if (!formData.cardNumber || !formData.cardName || !formData.expiryDate || !formData.cvv) {
      toast({
        title: "Missing Payment Information",
        description: "Please fill in all payment details",
        variant: "destructive"
      });
      return;
    }

    // Simulate order placement
    toast({
      title: "Order Placed Successfully!",
      description: `Your order of ₪${finalTotal.toFixed(2)} has been confirmed. Thank you for shopping with UNSEEN!`
    });

    // Clear cart and redirect
    setTimeout(() => {
      clearCart();
      navigate('/');
    }, 2000);
  };

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center py-16">
            <Package className="w-16 h-16 mx-auto text-warm-gray mb-4" />
            <h2 className="text-2xl font-light mb-4">Your cart is empty</h2>
            <p className="text-warm-gray mb-8">Add items to your cart before checking out</p>
            <Button className="primary-button" onClick={() => navigate('/collection/tops')}>
              Start Shopping
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        <h1 className="page-title mb-12">Checkout</h1>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Checkout Form - Left Side */}
            <div className="lg:col-span-2 space-y-8">
              {/* Personal Information */}
              <div className="checkout-section">
                <div className="flex items-center mb-6">
                  <User className="w-6 h-6 mr-3 text-accent-gold" />
                  <h2 className="checkout-section-title">Personal Information</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="checkout-label">First Name *</label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      className="checkout-input"
                      required
                    />
                  </div>
                  <div>
                    <label className="checkout-label">Last Name *</label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="checkout-input"
                      required
                    />
                  </div>
                  <div>
                    <label className="checkout-label">Email *</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="checkout-input"
                      required
                    />
                  </div>
                  <div>
                    <label className="checkout-label">Phone *</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="checkout-input"
                      placeholder="+972-"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Shipping Address */}
              <div className="checkout-section">
                <div className="flex items-center mb-6">
                  <MapPin className="w-6 h-6 mr-3 text-accent-gold" />
                  <h2 className="checkout-section-title">Shipping Address</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="checkout-label">Street Address *</label>
                    <input
                      type="text"
                      name="address"
                      value={formData.address}
                      onChange={handleInputChange}
                      className="checkout-input"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="checkout-label">City *</label>
                      <input
                        type="text"
                        name="city"
                        value={formData.city}
                        onChange={handleInputChange}
                        className="checkout-input"
                        required
                      />
                    </div>
                    <div>
                      <label className="checkout-label">Postal Code *</label>
                      <input
                        type="text"
                        name="postalCode"
                        value={formData.postalCode}
                        onChange={handleInputChange}
                        className="checkout-input"
                        required
                      />
                    </div>
                    <div>
                      <label className="checkout-label">Country *</label>
                      <input
                        type="text"
                        name="country"
                        value={formData.country}
                        onChange={handleInputChange}
                        className="checkout-input"
                        readOnly
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Shipping Method */}
              <div className="checkout-section">
                <div className="flex items-center mb-6">
                  <Package className="w-6 h-6 mr-3 text-accent-gold" />
                  <h2 className="checkout-section-title">Shipping Method</h2>
                </div>
                
                <div className="space-y-3">
                  <label className="shipping-option">
                    <input
                      type="radio"
                      name="shipping"
                      value="standard"
                      checked={shippingMethod === 'standard'}
                      onChange={(e) => setShippingMethod(e.target.value)}
                      className="mr-4"
                    />
                    <div className="flex-1">
                      <div className="font-bold text-accent-primary">Standard Shipping - ₪40</div>
                      <div className="text-sm text-accent-gray">Delivery in 4 business days</div>
                    </div>
                  </label>
                  
                  <label className="shipping-option">
                    <input
                      type="radio"
                      name="shipping"
                      value="express"
                      checked={shippingMethod === 'express'}
                      onChange={(e) => setShippingMethod(e.target.value)}
                      className="mr-4"
                    />
                    <div className="flex-1">
                      <div className="font-bold text-accent-primary">Express Shipping - ₪60</div>
                      <div className="text-sm text-accent-gray">Delivery in 2 business days</div>
                    </div>
                  </label>
                </div>
              </div>

              {/* Payment Information */}
              <div className="checkout-section">
                <div className="flex items-center mb-6">
                  <CreditCard className="w-6 h-6 mr-3 text-accent-gold" />
                  <h2 className="checkout-section-title">Payment Information</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="checkout-label">Card Number *</label>
                    <input
                      type="text"
                      name="cardNumber"
                      value={formData.cardNumber}
                      onChange={handleInputChange}
                      className="checkout-input"
                      placeholder="1234 5678 9012 3456"
                      maxLength="19"
                      required
                    />
                  </div>
                  <div>
                    <label className="checkout-label">Cardholder Name *</label>
                    <input
                      type="text"
                      name="cardName"
                      value={formData.cardName}
                      onChange={handleInputChange}
                      className="checkout-input"
                      placeholder="Name on card"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="checkout-label">Expiry Date *</label>
                      <input
                        type="text"
                        name="expiryDate"
                        value={formData.expiryDate}
                        onChange={handleInputChange}
                        className="checkout-input"
                        placeholder="MM/YY"
                        maxLength="5"
                        required
                      />
                    </div>
                    <div>
                      <label className="checkout-label">CVV *</label>
                      <input
                        type="text"
                        name="cvv"
                        value={formData.cvv}
                        onChange={handleInputChange}
                        className="checkout-input"
                        placeholder="123"
                        maxLength="4"
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Summary - Right Side */}
            <div className="lg:col-span-1">
              <div className="order-summary">
                <h3 className="order-summary-title mb-6">Order Summary</h3>
                
                {/* Cart Items */}
                <div className="space-y-4 mb-6 max-h-64 overflow-y-auto">
                  {cartItems.map((item) => (
                    <div key={`${item.id}-${item.selectedSize}-${item.selectedColor}`} className="flex gap-3">
                      <div className="w-16 h-16 bg-dark-tertiary border border-dark flex items-center justify-center">
                        {item.image ? (
                          <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="text-xs text-accent-gray">IMG</div>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-bold text-accent-primary">{item.name}</div>
                        <div className="text-xs text-accent-gray">{item.selectedColor} / {item.selectedSize}</div>
                        <div className="text-xs text-accent-gray">Qty: {item.quantity}</div>
                      </div>
                      <div className="text-sm font-bold text-accent-gold">₪{(item.price * item.quantity).toFixed(2)}</div>
                    </div>
                  ))}
                </div>

                {/* Price Breakdown */}
                <div className="space-y-3 border-t border-dark pt-4 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-accent-gray">Subtotal</span>
                    <span className="font-medium text-accent-primary">₪{cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-accent-gray">Shipping</span>
                    <span className="font-medium text-accent-primary">₪{shippingCost.toFixed(2)}</span>
                  </div>
                </div>

                <div className="border-t border-dark pt-4 mb-6">
                  <div className="flex justify-between">
                    <span className="text-lg font-bold text-accent-primary">Total</span>
                    <span className="text-lg font-bold text-accent-gold">₪{finalTotal.toFixed(2)}</span>
                  </div>
                </div>

                <Button type="submit" className="primary-button w-full" size="lg">
                  Place Order
                </Button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Checkout;
