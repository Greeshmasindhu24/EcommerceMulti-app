import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import AIChatbot from './components/AIChatbot';
import Home from './pages/Home';
import Cart from './pages/Cart';
import Auth from './pages/Auth';
import Orders from './pages/Orders';
import About from './pages/About';
import Contact from './pages/Contact';
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
    setCartItems((prev) => [...prev, product]);
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const handleLogout = () => {
    clearAuthStorage();
    setIsAuthenticated(false);
  };

  if (!authChecked) {
    return <div className="loading-state">Loading...</div>;
  }

  return (
    <Router>
      <div className="app-container">
        <Navbar isAuthenticated={isAuthenticated} onLogout={handleLogout} cartCount={cartItems.length} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home addToCart={addToCart} />} />
            <Route path="/shop" element={<Navigate to="/" replace />} />
            <Route path="/products/:category" element={<Home addToCart={addToCart} />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/cart" element={<Cart cartItems={cartItems} clearCart={clearCart} isAuthenticated={isAuthenticated} />} />
            <Route path="/auth" element={<Auth setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="/orders" element={<Orders isAuthenticated={isAuthenticated} onLogout={handleLogout} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer className="site-footer">
          <div className="container">
            <div className="footer-brand">
              <span className="nav-logo-icon">S</span>
              Style
            </div>
            <p>Online shopping powered by multi-agent AI.</p>
            <div className="footer-copy">
              &copy; {new Date().getFullYear()} Style. All rights reserved.
            </div>
          </div>
        </footer>

        <AIChatbot />
      </div>
    </Router>
  );
}

export default App;
