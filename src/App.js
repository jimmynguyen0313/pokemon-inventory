import React, { useState } from 'react';
import './App.css';
import ProductSearch from './components/ProductSearch';
import AddItem from './components/AddItem';
import InventoryList from './components/InventoryList';
import PortfolioValue from './components/PortfolioValue';

function App() {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [refreshInventory, setRefreshInventory] = useState(0);

  const handleProductSelected = (product) => {
    setSelectedProduct(product);
  };

  const handleItemAdded = () => {
    // Trigger refresh of inventory and portfolio value
    setRefreshInventory(refreshInventory + 1);
  };

  const handleItemChanged = () => {
    // Used by InventoryList when items are edited/deleted
    setRefreshInventory((prev) => prev + 1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔴 Pokemon Sealed Inventory</h1>
        <p>Track your booster boxes, elite trainer boxes, and more</p>
      </header>

      <main className="App-main">
        <PortfolioValue refreshTrigger={refreshInventory} />

        <div className="form-section">
          <ProductSearch onSelectProduct={handleProductSelected} />
          <AddItem selectedProduct={selectedProduct} onItemAdded={handleItemAdded} />
        </div>

        <InventoryList refreshTrigger={refreshInventory} onItemChanged={handleItemChanged} />
      </main>

      <footer className="App-footer">
        <p>Pokemon is a trademark of The Pokémon Company International. Data from Pokémon TCG API.</p>
      </footer>
    </div>
  );
}

export default App;

