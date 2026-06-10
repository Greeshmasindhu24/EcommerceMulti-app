import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerUser, saveAuthSession, API_URL } from '../api';

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
        setError(
          `Cannot reach the server (${API_URL}). ` +
          'If this is the live Render site, redeploy the frontend with REACT_APP_API_URL set to your Render backend URL. ' +
          'First request on Render free tier can take up to 60 seconds — try again.'
        );
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
        <h2>{isLogin ? 'Login to Style' : 'Create Account'}</h2>

        {error && <div className="form-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '8px', padding: '14px' }} disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="form-footer">
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <span onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? 'Register here' : 'Login here'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Auth;
