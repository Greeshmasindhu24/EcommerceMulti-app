import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerUser, saveAuthSession } from '../api';

const Auth = ({ setIsAuthenticated }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const data = await loginUser(email, password);
        saveAuthSession(data.access_token, data.email || email);
        setIsAuthenticated(true);
        navigate('/');
      } else {
        await registerUser(email, password);
        const data = await loginUser(email, password);
        saveAuthSession(data.access_token, data.email || email);
        setIsAuthenticated(true);
        navigate('/');
      }
    } catch (err) {
      if (!err.response) {
        setError('Cannot reach the server. Start the multi-agent backend: cd EcommerceMultiAgent/backend && python app.py');
      } else if (err.response.status >= 500) {
        setError('Server error — database connection may have timed out. Please try again.');
      } else {
        setError(err.response?.data?.msg || 'Authentication failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="form-container glass-panel">
        <h2 style={{ textAlign: 'center', marginBottom: '32px', fontSize: '2rem' }}>
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>

        {error && <div style={{ background: 'rgba(214, 48, 49, 0.1)', color: 'var(--danger)', padding: '12px', borderRadius: '8px', marginBottom: '24px', textAlign: 'center' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '16px', padding: '14px' }} disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '32px', color: 'var(--text-secondary)' }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span
            style={{ color: 'var(--accent)', cursor: 'pointer', fontWeight: 600 }}
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Auth;
