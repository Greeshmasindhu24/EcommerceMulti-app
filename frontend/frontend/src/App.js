import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import AIChatbot from './components/AIChatbot';
import Home from './pages/Home';
import Shop from './pages/Shop';
import Cart from './pages/Cart';
import Auth from './pages/Auth';
import Orders from './pages/Orders';
import About from './pages/About';
import Contact from './pages/Contact';
import ProductList from './pages/ProductList';
import { clearAuthStorage, verifyAuth } from './api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [cartItems, setCartItems] = useState([]);

  useEffect(() => {
    const checkSession = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setAuthChecked(true);
        return;
      }
      try {
        await verifyAuth();
        setIsAuthenticated(true);
      } catch {
        clearAuthStorage();
        setIsAuthenticated(false);
      } finally {
        setAuthChecked(true);
      }
    };
    checkSession();
  }, []);

  const addToCart = (product) => {
    setCartItems(prev => [...prev, product]);
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const handleLogout = () => {
    clearAuthStorage();
    setIsAuthenticated(false);
  };

  if (!authChecked) {
    return <div style={{ textAlign: 'center', padding: '120px' }}>Loading...</div>;
  }

  return (
    <Router>
      <Navbar isAuthenticated={isAuthenticated} onLogout={handleLogout} cartCount={cartItems.length} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/shop" element={<Shop addToCart={addToCart} />} />
        <Route path="/products/:category" element={<ProductList addToCart={addToCart} />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/cart" element={<Cart cartItems={cartItems} clearCart={clearCart} isAuthenticated={isAuthenticated} />} />
        <Route path="/auth" element={<Auth setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/orders" element={<Orders isAuthenticated={isAuthenticated} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <AIChatbot />
    </Router>
  );
}

export default App;
