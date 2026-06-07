import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div>
      <section className="hero">
        <div className="hero-glow"></div>
        <div className="container">
          <h1>Elevate Your Lifestyle<br/>With Premium Choices</h1>
          <p>Discover our exclusive collection of high-end fashion, cutting-edge electronics, and lifestyle products curated just for you.</p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <Link to="/shop" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: '1.1rem' }}>Shop Now</Link>
            <Link to="/auth" className="btn btn-outline" style={{ padding: '16px 32px', fontSize: '1.1rem' }}>Join the Club</Link>
          </div>
        </div>
      </section>

      <section className="container" style={{ padding: '80px 24px' }}>
        <div className="glass-panel" style={{ padding: '60px', textAlign: 'center', background: 'rgba(108, 92, 231, 0.05)' }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '24px' }}>Powered by Multi-Agent AI</h2>
          <p style={{ maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)' }}>
            Experience the future of shopping. Our intelligent agents seamlessly route your queries—whether you need sales recommendations, order tracking, or general support, we've got you covered 24/7. Try the chat widget in the bottom right corner!
          </p>
        </div>
      </section>
    </div>
  );
};

export default Home;
