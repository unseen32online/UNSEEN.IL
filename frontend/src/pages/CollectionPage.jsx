import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProductsByCategory } from '../mock';
import { ChevronDown } from 'lucide-react';
import { Button } from '../components/ui/button';

const CollectionPage = () => {
  const { category } = useParams();
  const products = getProductsByCategory(category);
  const [sortBy, setSortBy] = useState('featured');

  const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="mb-12">
          <h1 className="page-title">{categoryTitle}</h1>
          <p className="page-subtitle">
            {category === 'tops' 
              ? 'Essential tops designed for everyday comfort and style'
              : 'Premium pants crafted for the modern wardrobe'}
          </p>
        </div>

        {/* Filters */}
        <div className="flex justify-between items-center mb-8 pb-4 border-b border-soft-gray">
          <p className="text-warm-gray">
            {products.length} {products.length === 1 ? 'Product' : 'Products'}
          </p>
          <div className="flex items-center space-x-2">
            <label className="text-sm text-warm-gray">Sort by:</label>
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="filter-select"
            >
              <option value="featured">Featured</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="newest">Newest</option>
            </select>
          </div>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product) => (
            <Link 
              key={product.id} 
              to={`/product/${product.id}`}
              className="product-card group"
            >
              <div className="product-image-placeholder">
                {product.image ? (
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="placeholder-text">PRODUCT IMAGE</div>
                )}
                <div className="product-overlay">
                  <Button className="overlay-button">
                    View Details
                  </Button>
                </div>
              </div>
              <div className="product-info">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-price">₪{product.price}</p>
                <div className="flex space-x-1 mt-2">
                  {product.colors.map((color, idx) => (
                    <div
                      key={idx}
                      className="color-dot"
                      title={color}
                    />
                  ))}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CollectionPage;
