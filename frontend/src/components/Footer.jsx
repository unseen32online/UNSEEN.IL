import React from 'react';
import { Instagram, Facebook, Twitter } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-charcoal text-cream-white mt-24">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="col-span-1">
            <img 
              src="https://customer-assets.emergentagent.com/job_b445d7de-0eb2-4eae-9616-38092e60a3e6/artifacts/cmb2hfcf_Black%20White%20Bold%20Modern%20Clothing%20Brand%20Logo%20%281%29.png" 
              alt="UNSEEN" 
              className="h-8 mb-4 brightness-0 invert"
            />
            <p className="text-warm-gray text-sm leading-relaxed">
              Timeless style for everyday living. Crafted with care, designed for comfort.
            </p>
          </div>

          {/* Shop */}
          <div>
            <h4 className="footer-heading">Shop</h4>
            <ul className="space-y-3">
              <li><Link to="/collection/tops" className="footer-link">Tops</Link></li>
              <li><Link to="/collection/pants" className="footer-link">Pants</Link></li>
              <li><Link to="/collection/tops" className="footer-link">New Arrivals</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="footer-heading">Support</h4>
            <ul className="space-y-3">
              <li><Link to="/contact" className="footer-link">Contact Us</Link></li>
              <li><Link to="/privacy-policy" className="footer-link">Privacy Policy</Link></li>
              <li><Link to="/privacy-policy" className="footer-link">Shipping & Returns</Link></li>
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h4 className="footer-heading">Connect</h4>
            <div className="flex space-x-4 mt-4">
              <a href="#" className="social-icon">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="social-icon">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="social-icon">
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-warm-gray/30 mt-12 pt-8 text-center">
          <p className="text-warm-gray text-sm">
            © 2025 UNSEEN. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
