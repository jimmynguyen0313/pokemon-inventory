import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config';
import './AddItem.css';

export default function AddItem({ selectedProduct, onItemAdded }) {
  const [quantity, setQuantity] = useState(1);
  const [purchasePrice, setPurchasePrice] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch categories on component mount
  useEffect(() => {
    fetch(`${API_BASE}/categories`)
      .then(res => res.json())
      .then(data => {
        setCategories(data);
        if (data.length > 0) {
          setCategoryId(data[0].id.toString());
        }
      })
      .catch(err => console.error('Failed to load categories:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedProduct) {
      setError('Please select a product first');
      return;
    }

    if (!purchasePrice || parseFloat(purchasePrice) <= 0) {
      setError('Please enter a valid purchase price');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_BASE}/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: selectedProduct.id,
          quantity: parseInt(quantity),
          purchase_price: parseFloat(purchasePrice),
          category_id: categoryId ? parseInt(categoryId) : null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || data.error || 'Failed to add item');
        return;
      }

      setSuccess(`✅ Added ${quantity}x ${selectedProduct.name}`);
      setQuantity(1);
      setPurchasePrice('');
      if (categories.length > 0) {
        setCategoryId(categories[0].id.toString());
      }
      
      if (onItemAdded) {
        onItemAdded();
      }
    } catch (err) {
      setError('Error adding item: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-item">
      <h2>Add to Inventory</h2>
      
      {!selectedProduct ? (
        <p className="no-product">Select a product from search results above</p>
      ) : (
        <>
          <div className="selected-display">
            <p><strong>Product:</strong> {selectedProduct.name}</p>
            {selectedProduct.images_url && (
              <img src={selectedProduct.images_url} alt={selectedProduct.name} />
            )}
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="quantity">Quantity</label>
              <input
                id="quantity"
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="purchasePrice">Purchase Price ($)</label>
              <input
                id="purchasePrice"
                type="number"
                step="0.01"
                min="0"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                placeholder="e.g., 99.99"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
              >
                <option value="">-- Select Category --</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {error && <p className="error">{error}</p>}
            {success && <p className="success">{success}</p>}

            <button type="submit" disabled={loading || !selectedProduct}>
              {loading ? 'Adding...' : 'Add Item'}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
