import React, { useState, useEffect } from 'react';
import { getProducts } from '../api';
import ProductCard from '../components/ProductCard';

const Shop = ({ addToCart }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [category, setCategory] = useState('all');

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getProducts(category);
        setProducts(data);
      } catch (error) {
        console.error("Failed to fetch products:", error);
        setError('Unable to load products. Please check your backend server connection.');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [category]);

  return (
    <div className="container">
      <div className="page-header">
        <h1>Our Collection</h1>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px' }}>
          {['all', 'mobiles', 'laptops', 'electronics', 'fashion', 'beauty', 'gaming'].map(cat => (
            <button
              key={cat}
              className={`btn ${category === cat ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setCategory(cat)}
              style={{ textTransform: 'capitalize' }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px' }}>Loading products...</div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '80px', color: 'var(--danger)' }}>{error}</div>
      ) : (
        <div className="products-grid">
          {products.map(product => (
            <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Shop;
