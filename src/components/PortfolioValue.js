import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config';
import './PortfolioValue.css';

export default function PortfolioValue({ refreshTrigger }) {
  const [totalValue, setTotalValue] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTotalValue();
  }, [refreshTrigger]);

  const fetchTotalValue = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/total-value`);
      const data = await response.json();
      setTotalValue(data.total_value || 0);
    } catch (err) {
      console.error('Error fetching total value:', err);
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

  return (
    <div className="portfolio-value">
      <div className="value-card">
        <h2>Portfolio Value</h2>
        {loading ? (
          <p className="loading">Calculating...</p>
        ) : (
          <div className="value-display">
            <span className="amount">{formatPrice(totalValue)}</span>
            <p className="subtitle">Total collection value</p>
          </div>
        )}
      </div>
    </div>
  );
}
