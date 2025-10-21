import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="hero-section-with-image">
        <div className="hero-image-container">
          <img 
            src="https://customer-assets.emergentagent.com/job_unseen-daily/artifacts/kcm702xw_emrebey_09_09_25_0056.jpeg" 
            alt="UNSEEN Collection"
            className="hero-main-image"
          />
          <div className="hero-overlay"></div>
        </div>
        <div className="hero-content-overlay">
          <div className="max-w-7xl mx-auto px-6 py-32 md:py-48">
            <div className="max-w-3xl">
              <h1 className="hero-title">
                Everyday Essentials,
                <br />
                Timeless Style
              </h1>
              <p className="hero-subtitle">
                Discover our curated collection of casual clothing designed for comfort and crafted for the modern lifestyle.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mt-8">
                <Link to="/collection/tops">
                  <Button size="lg" className="primary-button w-full sm:w-auto">
                    Shop Tops
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link to="/collection/pants">
                  <Button size="lg" variant="outline" className="secondary-button w-full sm:w-auto">
                    Shop Pants
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Collections */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="section-title">Our Collections</h2>
            <p className="section-subtitle">
              Carefully designed pieces for your everyday wardrobe
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Tops Collection */}
            <Link to="/collection/tops" className="collection-card group">
              <div className="collection-image-placeholder">
                <div className="placeholder-text">TOPS COLLECTION</div>
              </div>
              <div className="collection-content">
                <h3 className="collection-title">Tops</h3>
                <p className="collection-description">
                  Essential tees, shirts, and layers for any occasion
                </p>
                <span className="collection-link">
                  Explore Collection <ArrowRight className="inline w-4 h-4 ml-1" />
                </span>
              </div>
            </Link>

            {/* Pants Collection */}
            <Link to="/collection/pants" className="collection-card group">
              <div className="collection-image-placeholder">
                <div className="placeholder-text">PANTS COLLECTION</div>
              </div>
              <div className="collection-content">
                <h3 className="collection-title">Pants</h3>
                <p className="collection-description">
                  From tailored chinos to relaxed fits, find your perfect pair
                </p>
                <span className="collection-link">
                  Explore Collection <ArrowRight className="inline w-4 h-4 ml-1" />
                </span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section className="py-24 bg-soft-gray">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="section-title">The UNSEEN Philosophy</h2>
          <p className="philosophy-text">
            We believe in creating clothing that transcends trends. Each piece is thoughtfully designed to blend seamlessly into your daily life, offering comfort without compromising on style. Our commitment is to quality, sustainability, and timeless design that you'll reach for season after season.
          </p>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-24">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h2 className="section-title">Stay Connected</h2>
          <p className="section-subtitle mb-8">
            Subscribe to receive updates on new arrivals and exclusive offers
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="newsletter-input"
            />
            <Button className="primary-button whitespace-nowrap">
              Subscribe
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
