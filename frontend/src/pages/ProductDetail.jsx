import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProductById } from '../mock';
import { useCart } from '../context/CartContext';
import { Button } from '../components/ui/button';
import { ChevronLeft, Check } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const product = getProductById(id);
  const { addToCart } = useCart();
  const { toast } = useToast();

  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');

  if (!product) {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <p>Product not found</p>
      </div>
    );
  }

  const handleAddToCart = () => {
    if (!selectedSize) {
      toast({
        title: "Please select a size",
        variant: "destructive"
      });
      return;
    }
    if (!selectedColor) {
      toast({
        title: "Please select a color",
        variant: "destructive"
      });
      return;
    }

    addToCart(product, selectedSize, selectedColor);
    toast({
      title: "Added to cart",
      description: `${product.name} has been added to your cart`
    });
  };

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-warm-gray hover:text-charcoal mb-8 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div>
            <div className="product-detail-image-placeholder">
              {product.image ? (
                <img 
                  src={product.image} 
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="placeholder-text">PRODUCT IMAGE</div>
              )}
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              {product.images && product.images.filter(img => img).length > 0 ? (
                product.images.filter(img => img).slice(0, 3).map((img, idx) => (
                  <div key={idx} className="product-thumbnail-placeholder cursor-pointer">
                    <img 
                      src={img} 
                      alt={`${product.name} ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))
              ) : (
                [1, 2, 3].map((idx) => (
                  <div key={idx} className="product-thumbnail-placeholder">
                    <div className="text-xs text-warm-gray">Image {idx}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Product Info */}
          <div>
            <h1 className="product-detail-title">{product.name}</h1>
            <p className="product-detail-price">₪{product.price}</p>
            <p className="product-detail-description">{product.description}</p>

            {/* Color Selection */}
            <div className="mt-8">
              <label className="product-option-label">Color</label>
              <div className="flex space-x-3 mt-3">
                {product.colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={`color-option ${selectedColor === color ? 'selected' : ''}`}
                  >
                    {selectedColor === color && (
                      <Check className="w-4 h-4" />
                    )}
                    {color}
                  </button>
                ))}
              </div>
            </div>

            {/* Size Selection */}
            <div className="mt-8">
              <label className="product-option-label">Size</label>
              <div className="grid grid-cols-4 gap-3 mt-3">
                {product.sizes.map((size) => (
                  <button
                    key={size}
                    onClick={() => setSelectedSize(size)}
                    className={`size-option ${selectedSize === size ? 'selected' : ''}`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            {/* Add to Cart */}
            <Button
              onClick={handleAddToCart}
              className="primary-button w-full mt-8"
              size="lg"
            >
              Add to Cart
            </Button>

            {/* Product Details */}
            <div className="mt-12 space-y-4">
              <div className="product-detail-section">
                <h3 className="product-detail-section-title">Details</h3>
                <ul className="product-detail-list">
                  <li>Made in Portugal</li>
                  <li>Oversize design</li>
                </ul>
              </div>
              <div className="product-detail-section">
                <h3 className="product-detail-section-title">Shipping & Returns</h3>
                <ul className="product-detail-list">
                  <li>Free shipping on orders over $100</li>
                  <li>30-day return policy</li>
                  <li>Ships within 2-3 business days</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
