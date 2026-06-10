import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { placeOrder } from '../api';

const Cart = ({ cartItems, clearCart, isAuthenticated }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('Credit Card');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [trackingNumber, setTrackingNumber] = useState(null);
  const navigate = useNavigate();

  const total = cartItems.reduce((sum, item) => sum + item.price, 0);
  const shipping = total > 5000 ? 0 : 500;
  const totalAmount = total + shipping;

  const customerName = `${firstName} ${lastName}`.trim();
  const shippingAddress = [address, city, zipCode].filter(Boolean).join(', ');

  const validateCustomerDetails = () => {
    if (!firstName.trim() || !lastName.trim() || !address.trim() || !city.trim() || !zipCode.trim()) {
      alert('Please fill in all shipping details: first name, last name, address, city, and ZIP code.');
      return false;
    }
    return true;
  };

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    if (!validateCustomerDetails()) return;

    setIsProcessing(true);
    try {
      const orderData = {
        total_amount: totalAmount,
        items: cartItems,
        payment_method: paymentMethod,
        customer_name: customerName,
        shipping_address: shippingAddress,
      };

      const response = await placeOrder(orderData);
      setTrackingNumber(response.tracking_number || null);
      setSuccess(true);
      clearCart();
    } catch (error) {
      console.error('Checkout failed:', error);
      const message = error.response?.data?.msg
        || error.response?.data?.error
        || error.message
        || 'Checkout failed. Please try again.';
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
        <h1 style={{ color: 'var(--aura-success)', marginBottom: '16px' }}>Order Placed Successfully!</h1>
        <p style={{ color: 'var(--aura-muted)', marginBottom: '12px' }}>Thank you for shopping with Style.</p>
        {customerName && (
          <p style={{ color: 'var(--aura-muted)', marginBottom: '12px' }}>
            Delivering to <strong>{customerName}</strong> at <strong>{shippingAddress}</strong>.
          </p>
        )}
        {trackingNumber && (
          <p style={{ color: 'var(--aura-muted)', marginBottom: '24px' }}>
            Tracking number: <strong>{trackingNumber}</strong>
          </p>
        )}
        <button type="button" className="btn btn-primary" onClick={() => navigate('/orders')}>View Orders</button>
      </div>
    );
  }

  return (
    <div className="container cart-page">
      <div className="page-header">
        <h1>Shopping Cart</h1>
      </div>

      {cartItems.length === 0 ? (
        <div className="empty-state">
          <p>Your cart is empty.</p>
          <p style={{ color: 'var(--aura-muted)', marginTop: '8px' }}>Subtotal ₹0.00</p>
          <button type="button" className="btn btn-primary" onClick={() => navigate('/')} style={{ marginTop: '24px' }}>
            Continue Shopping →
          </button>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items-column">
            {cartItems.map((item, index) => (
              <div key={index} className="cart-item glass-panel">
                <img src={item.image} alt={item.name} />
                <div className="cart-item-info">
                  <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>{item.name}</h3>
                  <div style={{ color: 'var(--aura-accent)', textTransform: 'uppercase', fontSize: '0.8rem', marginBottom: '16px' }}>{item.category}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>₹{item.price.toLocaleString('en-IN')}</div>
                </div>
              </div>
            ))}

            <div className="checkout-details glass-panel">
              <h2 className="checkout-page-title">Checkout</h2>

              <h3 className="checkout-step-title">1. Shipping Details</h3>
              <div className="form-row-2">
                <div className="form-group">
                  <label htmlFor="first-name">First Name</label>
                  <input
                    id="first-name"
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="First name"
                    autoComplete="given-name"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="last-name">Last Name</label>
                  <input
                    id="last-name"
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Last name"
                    autoComplete="family-name"
                  />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="address">Address</label>
                <input
                  id="address"
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Street address"
                  autoComplete="street-address"
                />
              </div>
              <div className="form-row-2">
                <div className="form-group">
                  <label htmlFor="city">City</label>
                  <input
                    id="city"
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="City"
                    autoComplete="address-level2"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="zip">ZIP / Postal Code</label>
                  <input
                    id="zip"
                    type="text"
                    value={zipCode}
                    onChange={(e) => setZipCode(e.target.value)}
                    placeholder="ZIP / Postal Code"
                    autoComplete="postal-code"
                  />
                </div>
              </div>

              <h3 className="checkout-step-title" style={{ marginTop: '24px' }}>2. Payment Method</h3>
              <div className="payment-options">
                {['Credit Card', 'PayPal', 'Cash on Delivery'].map((method) => (
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
          </div>

          <div className="cart-summary glass-panel">
            <h2 style={{ marginBottom: '24px' }}>Order Summary</h2>
            <div className="summary-row">
              <span>Subtotal</span>
              <span>₹{total.toLocaleString('en-IN')}</span>
            </div>
            <div className="summary-row">
              <span>Shipping</span>
              <span>{shipping === 0 ? 'Free' : `₹${shipping.toLocaleString('en-IN')}`}</span>
            </div>
            <div className="summary-total">
              <span>Total</span>
              <span>₹{totalAmount.toLocaleString('en-IN')}</span>
            </div>
            <p style={{ color: 'var(--aura-muted)', fontSize: '0.875rem', marginTop: '12px' }}>
              Shipping and taxes calculated at checkout.
            </p>
            <button
              type="button"
              className="btn btn-primary checkout-btn"
              onClick={handleCheckout}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Place Order'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
