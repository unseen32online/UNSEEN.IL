import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { Button } from '../components/ui/button';
import { Minus, Plus, Trash2, ShoppingBag } from 'lucide-react';

const Cart = () => {
  const navigate = useNavigate();
  const { cartItems, updateQuantity, removeFromCart, cartTotal } = useCart();

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center py-16">
            <ShoppingBag className="w-16 h-16 mx-auto text-warm-gray mb-4" />
            <h2 className="text-2xl font-light mb-4">Your cart is empty</h2>
            <p className="text-warm-gray mb-8">Start shopping to add items to your cart</p>
            <Link to="/collection/tops">
              <Button className="primary-button">Start Shopping</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        <h1 className="page-title mb-12">Shopping Cart</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-6">
            {cartItems.map((item) => (
              <div key={`${item.id}-${item.selectedSize}-${item.selectedColor}`} className="cart-item">
                <div className="cart-item-image-placeholder">
                  {item.image ? (
                    <img 
                      src={item.image} 
                      alt={item.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-xs text-warm-gray">Image</div>
                  )}
                </div>

                <div className="flex-1">
                  <h3 className="cart-item-name">{item.name}</h3>
                  <p className="cart-item-details">
                    {item.selectedColor} / {item.selectedSize}
                  </p>
                  <p className="cart-item-price">₪{item.price}</p>
                </div>

                <div className="flex flex-col items-end space-y-4">
                  <button
                    onClick={() => removeFromCart(item.id, item.selectedSize, item.selectedColor)}
                    className="cart-remove-button"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  <div className="quantity-control">
                    <button
                      onClick={() => updateQuantity(item.id, item.selectedSize, item.selectedColor, item.quantity - 1)}
                      className="quantity-button"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="quantity-display">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.selectedSize, item.selectedColor, item.quantity + 1)}
                      className="quantity-button"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="order-summary">
              <h3 className="order-summary-title">Order Summary</h3>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-warm-gray">Subtotal</span>
                  <span className="font-medium">₪{cartTotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-warm-gray">Shipping</span>
                  <span className="font-medium">Calculated at checkout</span>
                </div>
              </div>

              <div className="border-t border-soft-gray pt-4 mb-6">
                <div className="flex justify-between">
                  <span className="text-lg font-medium">Total</span>
                  <span className="text-lg font-medium">₪{cartTotal.toFixed(2)}</span>
                </div>
              </div>

              <Button type="submit" className="primary-button w-full mb-4" size="lg" onClick={() => navigate('/checkout')}>
                Proceed to Checkout
              </Button>

              <Link to="/collection/tops">
                <Button variant="outline" className="secondary-button w-full">
                  Continue Shopping
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
