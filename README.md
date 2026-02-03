# 🔴 Pokemon Inventory Management System

A full-stack web application for managing and tracking your Pokemon sealed product collection with real-time market valuations.

![React](https://img.shields.io/badge/React-19-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![Pokemon](https://img.shields.io/badge/Pokemon-TCG-yellow.svg)

## ✨ Features

- **📦 Product Search**: Find Pokemon booster boxes, elite trainer boxes, and sealed products
- **💰 Real-time Valuations**: Get current market prices from Pokemon Price Tracker API
- **📊 Portfolio Tracking**: Monitor your collection's total value and individual item performance
- **🏷️ Category Management**: Organize inventory with custom categories
- **➕ Easy Add/Remove**: Quickly add items with purchase price, quantity, and dates
- **🗑️ Item Management**: Delete items with confirmation to keep inventory clean
- **📱 Responsive Design**: Works great on desktop and mobile devices

## 🚀 Tech Stack

### Frontend
- **React 19** - Modern UI framework
- **Create React App** - Zero-config setup
- **CSS3** - Custom styling with grid layouts
- **Fetch API** - REST API communication

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLite** - Lightweight, optimized database
- **Pydantic** - Data validation and serialization
- **Uvicorn** - Lightning-fast ASGI server

### External APIs
- **Pokemon Price Tracker API** - Real-time market pricing data

## 🛠️ Installation & Setup

### Prerequisites
- **Node.js** (v14 or higher)
- **Python** (3.8 or higher)
- **Pokemon Price Tracker API Key** ([Get free key](https://www.pokemonpricetracker.com/api))

### 1. Clone the Repository
```bash
git clone https://github.com/jimmynguyen0313/pokemon-inventory.git
cd pokemon-inventory
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set your API key (replace with your actual key)
export POKEMON_PRICE_TRACKER_API_KEY=your_api_key_here
# On Windows: set POKEMON_PRICE_TRACKER_API_KEY=your_api_key_here

# Initialize database
python db_init.py

# (Optional) Seed with sample products
python sync_products.py --limit 50

# Start the backend server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# In a new terminal, navigate to project root
cd pokemon-inventory

# Install Node.js dependencies
npm install

# Start the development server
npm start
```

### 4. Open the Application
Visit **http://localhost:3000** in your browser!

## 📖 Usage

1. **Search Products**: Use the search bar to find Pokemon sealed products
2. **Add to Inventory**: Click on a product, enter quantity and purchase price, select category
3. **View Portfolio**: See your total collection value and individual item details
4. **Manage Items**: Delete items you no longer own using the delete button
5. **Track Performance**: Compare purchase prices with current market values

## 🏗️ Project Structure

```
pokemon-inventory/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── models.py           # Pydantic data models
│   ├── database.py         # SQLite connection management
│   ├── pokemon_api.py      # External API client
│   └── requirements.txt    # Python dependencies
├── src/                    # React frontend
│   ├── components/         # Reusable UI components
│   ├── App.js             # Main application component
│   └── index.js           # Application entry point
├── public/                 # Static assets
└── .github/               # GitHub configuration
    └── copilot-instructions.md  # AI assistant guidelines
```

## 🗄️ Database Schema

The application uses an optimized SQLite database with:

- **Products Table**: Cached Pokemon product data with market prices
- **Items Table**: Your personal inventory with purchase history
- **Categories Table**: Custom organization categories
- **Optimized Indexes**: Fast search and aggregation queries

## 🔌 API Endpoints

### Backend (Port 8000)
- `GET /products/search` - Search cached products
- `GET /items` - Get user inventory
- `POST /items` - Add item to inventory
- `DELETE /items/{id}` - Remove item from inventory
- `GET /categories` - List categories
- `POST /categories` - Create new category
- `GET /total-value` - Calculate portfolio value

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Environment Variables

Create a `.env` file in the backend directory:

```env
POKEMON_PRICE_TRACKER_API_KEY=your_api_key_here
```

## 🚀 Deployment

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy the build/ directory
```

### Backend (Railway/Render)
- Set `POKEMON_PRICE_TRACKER_API_KEY` environment variable
- Deploy the backend/ directory
- Run `python db_init.py` on first deployment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pokemon Price Tracker](https://www.pokemonpricetracker.com/) for market data
- [Create React App](https://create-react-app.dev/) for the frontend setup
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing Python framework

---

**Disclaimer**: Pokemon is a trademark of The Pokémon Company International. This project is not affiliated with or endorsed by The Pokémon Company.
