import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { placeOrder } from '../api';

const Cart = ({ cartItems, clearCart, isAuthenticated }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('Credit Card');
  const [customerName, setCustomerName] = useState('');
  const [shippingAddress, setShippingAddress] = useState('');
  const [trackingNumber, setTrackingNumber] = useState(null);
  const navigate = useNavigate();

  const total = cartItems.reduce((sum, item) => sum + item.price, 0);
  const shipping = total > 5000 ? 0 : 500;
  const totalAmount = total + shipping;

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    if (!customerName.trim() || !shippingAddress.trim()) {
      alert('Please enter your name and shipping address before checkout.');
      return;
    }

    setIsProcessing(true);
    try {
      const orderData = {
        total_amount: totalAmount,
        items: cartItems,
        payment_method: paymentMethod,
        customer_name: customerName,
        shipping_address: shippingAddress
      };

      const response = await placeOrder(orderData);
      setTrackingNumber(response.tracking_number || null);
      setSuccess(true);
      clearCart();
    } catch (error) {
      console.error("Checkout failed:", error);
      const message = error.response?.data?.msg
        || error.response?.data?.error
        || error.message
        || "Checkout failed. Please try again.";
      if (error.response?.status === 401) {
        alert('Your session expired. Please log in again and retry checkout.');
        navigate('/auth');
        return;
      }
      alert(message);
    } finally {
      setIsProcessing(false);
    }
  };

  if (success) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '120px 24px' }}>
        <h1 style={{ color: 'var(--success)', marginBottom: '16px' }}>Order Placed Successfully!</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Thank you for shopping with STYLE.</p>
        {customerName && <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>Order will be delivered to <strong>{customerName}</strong> at <strong>{shippingAddress}</strong>.</p>}
        {trackingNumber && <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Your tracking number is <strong>{trackingNumber}</strong>.</p>}
        <button className="btn btn-primary" onClick={() => navigate('/orders')}>View Orders</button>
      </div>
    );
  }

  return (
    <div className="container cart-page">
      <div className="page-header">
        <h1>Your Cart</h1>
      </div>

      {cartItems.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px', color: 'var(--text-secondary)' }}>
          <p>Your cart is empty.</p>
          <button className="btn btn-primary" onClick={() => navigate('/shop')} style={{ marginTop: '24px' }}>Go to Shop</button>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items-column">
            {cartItems.map((item, index) => (
              <div key={index} className="cart-item glass-panel">
                <img src={item.image} alt={item.name} />
                <div className="cart-item-info">
                  <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>{item.name}</h3>
                  <div style={{ color: 'var(--accent)', textTransform: 'uppercase', fontSize: '0.8rem', marginBottom: '16px' }}>{item.category}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>₹{item.price.toLocaleString('en-IN')}</div>
                </div>
              </div>
            ))}

            <div className="checkout-details glass-panel">
              <h2 style={{ marginBottom: '20px' }}>Delivery Details</h2>
              <div className="form-group">
                <label htmlFor="customer-name">Recipient Name</label>
                <input
                  id="customer-name"
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="Enter your full name"
                  autoComplete="name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="shipping-address">Shipping Address</label>
                <textarea
                  id="shipping-address"
                  value={shippingAddress}
                  onChange={(e) => setShippingAddress(e.target.value)}
                  placeholder="House no, street, city, state, PIN code"
                  rows={4}
                />
              </div>
            </div>
          </div>

          <div className="cart-summary glass-panel">
            <h2 style={{ marginBottom: '24px' }}>Order Summary</h2>
            <div className="summary-row">
              <span>Subtotal ({cartItems.length} items)</span>
              <span>₹{total.toLocaleString('en-IN')}</span>
            </div>
            <div className="summary-row">
              <span>Shipping</span>
              <span>{shipping === 0 ? 'Free' : '₹500'}</span>
            </div>
            <div className="summary-row">
              <span>Tax (Included)</span>
              <span>₹0</span>
            </div>

            <div className="payment-methods">
              <span className="payment-label">Payment Method</span>
              <div className="payment-options">
                {['Credit Card', 'Cash on Delivery'].map(method => (
                  <button
                    key={method}
                    type="button"
                    className={`payment-option ${paymentMethod === method ? 'active' : ''}`}
                    onClick={() => setPaymentMethod(method)}
                  >
                    {method}
                  </button>
                ))}
              </div>
            </div>

            <div className="summary-total">
              <span>Total</span>
              <span>₹{totalAmount.toLocaleString('en-IN')}</span>
            </div>
            <button
              className="btn btn-primary checkout-btn"
              onClick={handleCheckout}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : `Checkout with ${paymentMethod}`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
