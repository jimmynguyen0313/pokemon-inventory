import React, { useState, useEffect } from 'react';
import './InventoryList.css';

export default function InventoryList({ refreshTrigger, onItemChanged }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchItems();
  }, [refreshTrigger]);

  const fetchItems = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/items');
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError('Failed to load inventory: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/items/${itemId}`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (response.ok) {
        fetchItems();
        if (onItemChanged) onItemChanged();
      } else {
        setError(data.detail || 'Failed to delete item');
      }
    } catch (err) {
      setError('Error deleting item: ' + err.message);
    }
  };

  if (loading) {
    return <div className="inventory">Loading inventory...</div>;
  }

  if (error) {
    return <div className="inventory error">{error}</div>;
  }

  if (items.length === 0) {
    return (
      <div className="inventory">
        <h2>Your Inventory</h2>
        <p className="empty">No items yet. Add some Pokemon sets above!</p>
      </div>
    );
  }

  return (
    <div className="inventory">
      <h2>Your Inventory ({items.length} items)</h2>
      
      <div className="inventory-grid">
        {items.map((item) => (
          <div key={item.id} className="inventory-card">
            <div className="card-header">
              {item.images_url && (
                <img src={item.images_url} alt={item.name} className="product-image" />
              )}
            </div>

            <div className="card-content">
              <h3>{item.name}</h3>
              
              <div className="info-row">
                <span className="label">Set:</span>
                <span className="value">{item.set_name || 'Unknown'}</span>
              </div>

              <div className="info-row">
                <span className="label">Quantity:</span>
                <span className="value">{item.quantity}x</span>
              </div>

              <div className="info-row">
                <span className="label">Category:</span>
                <span className="category-badge">{item.category_name || 'Uncategorized'}</span>
              </div>

              <div className="price-section">
                <div className="price-row">
                  <span className="label">Purchase Price:</span>
                  <span className="value">{formatPrice(item.purchase_price)}</span>
                </div>

                {item.market_value ? (
                  <div className="price-row">
                    <span className="label">Market Value:</span>
                    <span className="value highlight">{formatPrice(item.market_value)}</span>
                  </div>
                ) : (
                  <div className="price-row">
                    <span className="label">Fallback Value:</span>
                    <span className="value">{formatPrice(item.purchase_price)}</span>
                  </div>
                )}

                <div className="total-value">
                  <span className="label">Total:</span>
                  <span className="amount">
                    {formatPrice((item.market_value || item.purchase_price) * item.quantity)}
                  </span>
                </div>
              </div>

              <div className="purchase-date">
                Added: {new Date(item.purchase_date).toLocaleDateString()}
              </div>

              <button 
                className="delete-btn" 
                onClick={() => handleDelete(item.id)}
                title="Delete this item"
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
