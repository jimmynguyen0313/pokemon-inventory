import React, { useState, useEffect } from 'react';
import './ProductSearch.css';

export default function ProductSearch({ onSelectProduct }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Debounce search term - only update after user stops typing for 300ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Perform search when debounced term changes
  useEffect(() => {
    if (!debouncedSearchTerm.trim()) {
      setResults([]);
      return;
    }

    handleSearch(debouncedSearchTerm);
  }, [debouncedSearchTerm]);

  const handleSearch = async (query) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/products/search?name=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error searching products:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProduct = (product) => {
    setSelectedProduct(product);
    onSelectProduct(product);
    setSearchTerm('');
    setResults([]);
  };

  return (
    <div className="product-search">
      <h2>Search Pokemon Sets</h2>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by set name (e.g., Scarlet, Violet)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        {loading && <span className="loading-spinner">🔄</span>}
      </div>

      {selectedProduct && (
        <div className="selected-product">
          <h3>Selected: {selectedProduct.name}</h3>
          {selectedProduct.images_url && (
            <img src={selectedProduct.images_url} alt={selectedProduct.name} />
          )}
          <button onClick={() => setSelectedProduct(null)}>Change</button>
        </div>
      )}

      {results.length > 0 && (
        <div className="results">
          <h3>Results ({results.length})</h3>
          <ul className="product-list">
            {results.map((product) => (
              <li key={product.id} className="product-item">
                <div className="product-info">
                  <h4>{product.name}</h4>
                  <p className="set-name">{product.set_name}</p>
                  {product.release_date && (
                    <p className="release-date">Released: {product.release_date}</p>
                  )}
                  {product.description && (
                    <p className="card-count">{product.description} cards</p>
                  )}
                </div>
                {product.images_url && (
                  <img src={product.images_url} alt={product.name} className="product-logo" />
                )}
                <button onClick={() => handleSelectProduct(product)}>Select</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
