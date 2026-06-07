import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOrders } from '../api';

const Orders = ({ isAuthenticated }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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
        console.error("Failed to fetch orders:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated, navigate]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '120px' }}>Loading orders...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Your Orders</h1>
      </div>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px', color: 'var(--text-secondary)' }}>
          <p>You haven't placed any orders yet.</p>
          <button className="btn btn-primary" onClick={() => navigate('/shop')} style={{ marginTop: '24px' }}>Start Shopping</button>
        </div>
      ) : (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          {orders.map((order) => (
            <div key={order.id} className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem' }}>Order #{order.id}</h3>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{new Date(order.date).toLocaleString()}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: 'var(--accent)', fontWeight: 600 }}>{order.status}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>₹{order.total.toLocaleString('en-IN')}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gap: '10px', marginBottom: '20px' }}>
                {order.customer_name && <div><strong>Customer:</strong> {order.customer_name}</div>}
                {order.shipping_address && <div><strong>Delivery Address:</strong> {order.shipping_address}</div>}
                {order.tracking_number && <div><strong>Tracking Number:</strong> {order.tracking_number}</div>}
              </div>

              <div>
                <h4 style={{ marginBottom: '12px', fontSize: '1rem' }}>Items:</h4>
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
