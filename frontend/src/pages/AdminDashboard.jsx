import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Package, DollarSign, TrendingUp, Users, Search, Filter, LogOut } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchEmail, setSearchEmail] = useState('');
  const [adminUsername, setAdminUsername] = useState('');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('admin_token');
    const username = localStorage.getItem('admin_username');
    
    if (!token) {
      navigate('/admin/login');
      return;
    }

    try {
      // Verify token with backend
      await axios.get(`${BACKEND_URL}/api/admin/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setAdminUsername(username);
      fetchAnalytics();
      fetchOrders();
    } catch (error) {
      console.error('Auth verification failed:', error);
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_username');
      navigate('/admin/login');
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return {
      'Authorization': `Bearer ${token}`
    };
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    navigate('/admin/login');
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/admin/analytics`, {
        headers: getAuthHeaders()
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      if (error.response?.status === 401) {
        handleLogout();
      }
    }
  };

  const fetchOrders = async (status = null, email = null) => {
    try {
      let url = `${BACKEND_URL}/api/orders?limit=50`;
      if (status && status !== 'all') {
        url += `&status=${status}`;
      }
      if (email) {
        url += `&customer_email=${email}`;
      }
      const response = await axios.get(url);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilter = (status) => {
    setSelectedStatus(status);
    fetchOrders(status, searchEmail);
  };

  const handleSearch = () => {
    fetchOrders(selectedStatus !== 'all' ? selectedStatus : null, searchEmail);
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await axios.patch(`${BACKEND_URL}/api/orders/${orderId}`, {
        status: newStatus
      });
      // Refresh orders
      fetchOrders(selectedStatus !== 'all' ? selectedStatus : null, searchEmail);
      fetchAnalytics();
    } catch (error) {
      console.error('Error updating order status:', error);
      alert('Failed to update order status');
    }
  };

  const getStatusBadgeClass = (status) => {
    const classes = {
      pending_payment: 'bg-yellow-500/20 text-yellow-500',
      payment_confirmed: 'bg-green-500/20 text-green-500',
      processing: 'bg-blue-500/20 text-blue-500',
      shipped: 'bg-purple-500/20 text-purple-500',
      delivered: 'bg-green-600/20 text-green-600',
      cancelled: 'bg-red-500/20 text-red-500'
    };
    return classes[status] || 'bg-accent-gray/20 text-accent-gray';
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

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="animate-pulse">
            <div className="h-8 bg-dark-tertiary rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-dark-tertiary rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6">
        <h1 className="page-title mb-8">Admin Dashboard</h1>

        {/* Analytics Cards */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-dark-secondary border border-dark p-6">
              <div className="flex items-center justify-between mb-4">
                <Package className="w-8 h-8 text-accent-gold" />
              </div>
              <div className="text-3xl font-bold text-accent-primary mb-2">
                {analytics.total_orders}
              </div>
              <div className="text-sm text-accent-gray">Total Orders</div>
            </div>

            <div className="bg-dark-secondary border border-dark p-6">
              <div className="flex items-center justify-between mb-4">
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-accent-primary mb-2">
                ₪{analytics.total_revenue.toFixed(2)}
              </div>
              <div className="text-sm text-accent-gray">Total Revenue</div>
            </div>

            <div className="bg-dark-secondary border border-dark p-6">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-accent-primary mb-2">
                {analytics.orders_by_status.processing || 0}
              </div>
              <div className="text-sm text-accent-gray">Processing Orders</div>
            </div>

            <div className="bg-dark-secondary border border-dark p-6">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-purple-500" />
              </div>
              <div className="text-3xl font-bold text-accent-primary mb-2">
                {analytics.orders_by_status.delivered || 0}
              </div>
              <div className="text-sm text-accent-gray">Delivered Orders</div>
            </div>
          </div>
        )}

        {/* Popular Products */}
        {analytics && analytics.popular_products.length > 0 && (
          <div className="bg-dark-secondary border border-dark p-6 mb-8">
            <h2 className="text-xl font-bold text-accent-primary mb-4">Popular Products</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {analytics.popular_products.slice(0, 6).map((product, index) => (
                <div key={index} className="flex justify-between items-center p-4 bg-dark-tertiary border border-dark">
                  <div>
                    <div className="font-bold text-accent-primary">{product.name}</div>
                    <div className="text-sm text-accent-gray">Sold: {product.total_quantity}</div>
                  </div>
                  <div className="text-accent-gold font-bold">
                    ₪{product.total_revenue.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Orders List */}
        <div className="bg-dark-secondary border border-dark p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <h2 className="text-xl font-bold text-accent-primary">Recent Orders</h2>
            
            <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
              {/* Search by Email */}
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder="Search by email..."
                  value={searchEmail}
                  onChange={(e) => setSearchEmail(e.target.value)}
                  className="checkout-input"
                />
                <Button onClick={handleSearch} className="primary-button">
                  <Search className="w-4 h-4" />
                </Button>
              </div>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => handleStatusFilter(e.target.value)}
                className="checkout-input"
              >
                <option value="all">All Status</option>
                <option value="pending_payment">Pending Payment</option>
                <option value="payment_confirmed">Payment Confirmed</option>
                <option value="processing">Processing</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark">
                  <th className="text-left p-3 text-accent-gray font-medium">Order #</th>
                  <th className="text-left p-3 text-accent-gray font-medium">Customer</th>
                  <th className="text-left p-3 text-accent-gray font-medium">Date</th>
                  <th className="text-left p-3 text-accent-gray font-medium">Total</th>
                  <th className="text-left p-3 text-accent-gray font-medium">Status</th>
                  <th className="text-left p-3 text-accent-gray font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} className="border-b border-dark hover:bg-dark-tertiary">
                    <td className="p-3 text-accent-primary font-bold">{order.order_number}</td>
                    <td className="p-3">
                      <div className="text-accent-primary">{order.customer_info.first_name} {order.customer_info.last_name}</div>
                      <div className="text-sm text-accent-gray">{order.customer_info.email}</div>
                    </td>
                    <td className="p-3 text-accent-gray">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-accent-gold font-bold">₪{order.total.toFixed(2)}</td>
                    <td className="p-3">
                      <span className={`px-3 py-1 text-xs font-bold ${getStatusBadgeClass(order.status)}`}>
                        {getStatusText(order.status)}
                      </span>
                    </td>
                    <td className="p-3">
                      <select
                        value={order.status}
                        onChange={(e) => updateOrderStatus(order.id, e.target.value)}
                        className="text-xs border border-dark bg-dark-tertiary text-accent-primary p-2"
                      >
                        <option value="pending_payment">Pending Payment</option>
                        <option value="payment_confirmed">Payment Confirmed</option>
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="delivered">Delivered</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {orders.length === 0 && (
            <div className="text-center py-8 text-accent-gray">
              No orders found
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
