import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOrders, clearAuthStorage } from '../api';

const Orders = ({ isAuthenticated, onLogout }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('email') || 'Not available';

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    const fetchOrders = async () => {
      try {
        const data = await getOrders();
        setOrders(data);
      } catch (error) {
        console.error('Failed to fetch orders:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated, navigate]);

  const handleSignOut = () => {
    clearAuthStorage();
    if (onLogout) onLogout();
    navigate('/auth');
  };

  if (loading) {
    return <div className="loading-state">Loading orders...</div>;
  }

  return (
    <div className="container" style={{ padding: '48px 24px' }}>
      <div className="account-header">
        <h1 className="checkout-page-title" style={{ margin: 0 }}>Your Account</h1>
        <button type="button" className="btn btn-outline" onClick={handleSignOut}>Sign Out</button>
      </div>

      <div className="glass-panel profile-card">
        <h3>Profile</h3>
        <p>Email: <strong>{userEmail}</strong></p>
      </div>

      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: '24px' }}>Order History</h2>

      {orders.length === 0 ? (
        <div className="empty-state glass-panel">
          <p>You haven&apos;t placed any orders yet.</p>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/')} style={{ marginTop: '24px' }}>
            Start Shopping
          </button>
        </div>
      ) : (
        <div style={{ maxWidth: '800px' }}>
          {orders.map((order) => (
            <div key={order.id} className="glass-panel order-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--aura-border)', paddingBottom: '16px', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem' }}>Order #{order.id}</h3>
                  <div style={{ color: 'var(--aura-muted)', fontSize: '0.9rem' }}>{new Date(order.date).toLocaleString()}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: 'var(--aura-accent)', fontWeight: 600 }}>{order.status}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>₹{order.total.toLocaleString('en-IN')}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gap: '10px', marginBottom: '20px' }}>
                {order.customer_name && <div><strong>Customer:</strong> {order.customer_name}</div>}
                {order.shipping_address && <div><strong>Delivery Address:</strong> {order.shipping_address}</div>}
                {order.tracking_number && <div><strong>Tracking Number:</strong> {order.tracking_number}</div>}
              </div>

              <div>
                <h4 style={{ marginBottom: '12px', fontSize: '1rem' }}>Items</h4>
                {order.items.map((item, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '16px', marginBottom: '12px', alignItems: 'center' }}>
                    <img src={item.image} alt={item.name} style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover' }} />
                    <div style={{ flex: 1 }}>{item.name}</div>
                    <div style={{ fontWeight: 600 }}>₹{item.price.toLocaleString('en-IN')}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Orders;
