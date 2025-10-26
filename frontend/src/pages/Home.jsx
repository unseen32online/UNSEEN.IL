import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Instagram } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Home = () => {
  const { toast } = useToast();
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);

  const handleNewsletterSubmit = async (e) => {
    e.preventDefault();
    
    if (!newsletterEmail || !/\S+@\S+\.\S+/.test(newsletterEmail)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive"
      });
      return;
    }

    setIsSubscribing(true);

    try {
      const response = await axios.post(`${BACKEND_URL}/api/newsletter/subscribe`, {
        email: newsletterEmail
      });

      if (response.data.success) {
        toast({
          title: "Welcome to UNSEEN FAM! 🎉",
          description: response.data.message
        });
        setNewsletterEmail('');
      }
    } catch (error) {
      console.error('Newsletter subscription error:', error);
      toast({
        title: "Subscription Failed",
        description: "Please try again later",
        variant: "destructive"
      });
    } finally {
      setIsSubscribing(false);
    }
  };
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="hero-section-with-image">
        <div className="hero-image-container">
          <img 
            src="https://customer-assets.emergentagent.com/job_unseen-daily/artifacts/0kaglgn2_emrebey_09_09_25_0057.jpeg" 
            alt="UNSEEN Collection"
            className="hero-main-image"
          />
          <div className="hero-overlay"></div>
        </div>
        <div className="hero-content-overlay">
          <div className="max-w-7xl mx-auto px-6 pb-8 md:pb-12 w-full">
            <div className="max-w-2xl mx-auto text-center">
              <h1 className="hero-title-centered">
                Everyday Essentials,
                <br />
                Timeless Style
              </h1>
              <p className="hero-subtitle-centered">
                Discover our curated collection of casual clothing designed for comfort and crafted for the modern lifestyle.
              </p>
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
                <img 
                  src="https://customer-assets.emergentagent.com/job_unseen-daily/artifacts/xiotp9h5_emrebey_09_09_25_0134.jpeg" 
                  alt="Tops Collection"
                  className="w-full h-full object-cover"
                />
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
                <img 
                  src="https://customer-assets.emergentagent.com/job_unseen-daily/artifacts/8wgzlv16_emrebey_09_09_25_0011.jpeg" 
                  alt="Shorts Collection"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="collection-content">
                <h3 className="collection-title">Shorts</h3>
                <p className="collection-description">
                  From bandana patterns to streetwear essentials
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
            We are international streetwear brand that offers uncompromising luxury clothes. Our commitment is to quality, sustainability, and timeless design that you'll reach for season after season.
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

      {/* Instagram Banner */}
      <section className="instagram-banner">
        <a 
          href="https://www.instagram.com/unseen.il/" 
          target="_blank" 
          rel="noopener noreferrer"
          className="instagram-banner-link"
        >
          <div className="instagram-banner-content">
            <Instagram className="instagram-icon" />
            <div>
              <h3 className="instagram-banner-title">Follow Us on Instagram</h3>
              <p className="instagram-banner-subtitle">@unseen.il - Join our community for exclusive drops & behind the scenes</p>
            </div>
            <ArrowRight className="instagram-arrow" />
          </div>
        </a>
      </section>
    </div>
  );
};

export default Home;
