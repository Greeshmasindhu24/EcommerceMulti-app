import React from 'react';

const ProductCard = ({ product, onAddToCart }) => {
  return (
    <div className="product-card glass-panel">
      <img src={product.image} alt={product.name} className="product-image" />
      <div className="product-info">
        <span className="product-category">{product.category}</span>
        <h3 className="product-title">{product.name}</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px', flex: 1 }}>
          {(product.description || '').substring(0, 80)}...
        </p>
        <div className="product-footer">
          <span className="product-price">₹{product.price.toLocaleString('en-IN')}</span>
          <button className="btn btn-primary" onClick={() => onAddToCart(product)}>Add to Cart</button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
