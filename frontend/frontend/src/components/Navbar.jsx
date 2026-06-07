import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = ({ isAuthenticated, onLogout, cartCount }) => {
  const location = useLocation();
  const path = location.pathname;

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="nav-brand">STYLE<span>.</span></Link>
        <div className="nav-links">
          <Link to="/" className={path === '/' ? 'active' : ''}>Home</Link>
          <Link to="/shop" className={path === '/shop' || path.startsWith('/products') ? 'active' : ''}>Shop</Link>
          <Link to="/about" className={path === '/about' ? 'active' : ''}>About</Link>
          <Link to="/contact" className={path === '/contact' ? 'active' : ''}>Contact</Link>
          <Link to="/agent-info" className={path === '/agent-info' ? 'active' : ''}>AI Agents</Link>
          <Link to="/cart" className={path === '/cart' ? 'active' : ''}>Cart ({cartCount})</Link>
          {isAuthenticated ? (
            <>
              <Link to="/orders" className={path === '/orders' ? 'active' : ''}>Orders</Link>
              <button onClick={onLogout} className="btn btn-outline" style={{ padding: '6px 16px', fontSize: '0.9rem' }}>Logout</button>
            </>
          ) : (
            <Link to="/auth" className="btn btn-primary" style={{ padding: '6px 16px', fontSize: '0.9rem' }}>Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
