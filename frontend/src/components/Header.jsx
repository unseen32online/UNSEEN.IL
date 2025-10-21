import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Menu, X } from 'lucide-react';
import { useCart } from '../context/CartContext';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { cartCount } = useCart();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-dark-bg border-b border-dark">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_b445d7de-0eb2-4eae-9616-38092e60a3e6/artifacts/cmb2hfcf_Black%20White%20Bold%20Modern%20Clothing%20Brand%20Logo%20%281%29.png" 
              alt="UNSEEN" 
              className="h-8 md:h-10 brightness-0 invert"
            />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/collection/tops" className="nav-link">Tops</Link>
            <Link to="/collection/pants" className="nav-link">Pants</Link>
          </nav>

          {/* Cart Icon */}
          <div className="flex items-center space-x-4">
            <Link to="/cart" className="relative cart-icon">
              <ShoppingBag className="w-6 h-6" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-accent-gold text-dark-bg text-xs font-black w-5 h-5 flex items-center justify-center rounded-full">
                  {cartCount}
                </span>
              )}
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-accent-primary"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden mt-4 pb-4 flex flex-col space-y-4 border-t border-dark pt-4">
            <Link to="/" className="nav-link" onClick={() => setIsMenuOpen(false)}>Home</Link>
            <Link to="/collection/tops" className="nav-link" onClick={() => setIsMenuOpen(false)}>Tops</Link>
            <Link to="/collection/pants" className="nav-link" onClick={() => setIsMenuOpen(false)}>Pants</Link>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
