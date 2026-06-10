import React, { useState, useEffect } from 'react';
import { getProducts } from '../api';
import ProductCard from '../components/ProductCard';

const Shop = ({ addToCart }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState('default');

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getProducts(category);
        setProducts(data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
        setError('Unable to load products. Please check your backend server connection.');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [category]);

  const sortedProducts = [...products].sort((a, b) => {
    if (sortBy === 'price-low') return a.price - b.price;
    if (sortBy === 'price-high') return b.price - a.price;
    return 0;
  });

  return (
    <div className="container">
      <div className="page-header">
        <h1>All Products ({products.length})</h1>
        <div className="filter-bar">
          {['all', 'mobiles', 'laptops', 'electronics', 'fashion', 'beauty', 'gaming'].map((cat) => (
            <button
              key={cat}
              type="button"
              className={`btn ${category === cat ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
        <div style={{ marginTop: '20px' }}>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              padding: '10px 16px',
              border: '1px solid var(--aura-border)',
              borderRadius: '8px',
              fontFamily: 'inherit',
              background: 'white',
            }}
          >
            <option value="default">Default Sorting</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading products...</div>
      ) : error ? (
        <div className="loading-state" style={{ color: 'var(--aura-danger)' }}>{error}</div>
      ) : (
        <div className="products-grid">
          {sortedProducts.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Shop;
