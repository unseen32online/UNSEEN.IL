import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { useToast } from '../hooks/use-toast';
import { Lock, User } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminLogin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      toast({
        title: "Missing Information",
        description: "Please enter both username and password",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post(`${BACKEND_URL}/api/admin/login`, formData);
      
      // Store token in localStorage
      localStorage.setItem('admin_token', response.data.access_token);
      localStorage.setItem('admin_username', response.data.username);
      
      toast({
        title: "Login Successful",
        description: `Welcome back, ${response.data.username}!`
      });

      // Redirect to admin dashboard
      setTimeout(() => {
        navigate('/admin');
      }, 1000);
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Invalid username or password",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-16 flex items-center justify-center">
      <div className="w-full max-w-md px-6">
        <div className="bg-dark-secondary border border-dark p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-gold/10 border border-accent-gold mb-4">
              <Lock className="w-8 h-8 text-accent-gold" />
            </div>
            <h1 className="text-3xl font-bold text-accent-primary mb-2">ADMIN LOGIN</h1>
            <p className="text-accent-gray">Enter your credentials to access the dashboard</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="checkout-label flex items-center mb-2">
                <User className="w-4 h-4 mr-2" />
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="checkout-input"
                placeholder="Enter your username"
                required
                autoComplete="username"
              />
            </div>

            <div>
              <label className="checkout-label flex items-center mb-2">
                <Lock className="w-4 h-4 mr-2" />
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="checkout-input"
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>

            <Button 
              type="submit" 
              className="primary-button w-full" 
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          {/* Info */}
          <div className="mt-6 text-center text-sm text-accent-gray">
            <p>Authorized personnel only</p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <button
            onClick={() => navigate('/')}
            className="text-accent-gray hover:text-accent-primary transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
