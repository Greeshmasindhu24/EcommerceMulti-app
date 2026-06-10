import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProducts } from '../api';
import ProductCard from '../components/ProductCard';

export default function ProductList({ addToCart }) {
  const { category } = useParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const data = await getProducts(category);
        setProducts(data || []);
      } catch (err) {
        console.error('Error fetching products', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [category]);

  if (loading) {
    return <div className="loading-state">Loading {category}...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
          <Link to="/products/all" className="link-accent" style={{ display: "inline-block", marginBottom: "12px" }}>
          ← Back to Home
        </Link>
        <h1 style={{ textTransform: 'capitalize' }}>{category}</h1>
      </div>

      {products.length === 0 ? (
        <div className="empty-state">No products found in this category.</div>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
          ))}
        </div>
      )}
    </div>
  );
}
