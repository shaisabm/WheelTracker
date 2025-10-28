# Wheel Strategy Tracker

A professional dashboard for tracking options trading using the wheel strategy. Built with Django (backend) and SvelteKit (frontend).

## Features

### Position Tracking
- Track all your wheel strategy positions (puts and calls)
- Record comprehensive trade data including:
  - Open/close dates
  - Stock ticker and set number
  - Strike price and premium received
  - Number of contracts
  - Fees (open and close)
  - Assignment status
  - Notes

### Calculated Metrics
The dashboard automatically calculates:
- **Profit/Loss**: Net P/L after premiums and fees
- **AR% if Held to Expiration**: Annualized return if position is held through expiration
- **AR% of Closed Trade**: Actual annualized return for closed positions
- **AR% on Realized Premium**: Potential AR% if closed at current price (open positions)
- **AR% on Remaining Premium**: AR% on remaining value until expiration
- **Percent Premium Earned**: % of premium already captured
- **Set Break Even Price**: Break-even calculation for put sets
- **Collateral Requirement**: Capital at risk for each position
- **Days to Expiration**: Remaining days until expiration
- **Days in Trade**: Total days held

### Portfolio Summary
- Total positions (open vs closed)
- Total P/L across all closed positions
- Total premium collected
- Total collateral at risk
- Average annualized return for closed trades
- List of all stocks traded

### Yahoo Finance Integration
- Fetch current option prices from Yahoo Finance
- Update individual positions or all open positions at once
- Automatically calculates mid-price from bid/ask spread

### Filtering & Organization
- Filter by stock ticker
- Filter by option type (Put/Call)
- Filter by status (Open/Closed)
- Organize positions by set number for tracking wheels

## Setup

### Backend (Django)

1. Navigate to the project directory:
```bash
cd WheelTracker
```

2. Install Python dependencies (already installed):
```bash
pip install djangorestframework django-cors-headers yfinance
```

3. The database migrations have already been created and applied.

4. Create a superuser for Django admin (optional):
```bash
python manage.py createsuperuser
```

5. Start the Django development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/`

### Frontend (Svelte)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the Vite development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173/`

## Usage

### Adding a Position

1. Click the "+ New Position" button
2. Fill in the required fields:
   - **Open Date**: Date you opened the contract
   - **Stock**: Ticker symbol (e.g., AAPL, TSLA)
   - **Set Number**: Track different wheel cycles (default: 1)
   - **Expiration**: Contract expiration date
   - **Type**: Put (P) or Call (C)
   - **# Contracts**: Number of contracts
   - **Strike**: Strike price
   - **Premium**: Premium received per contract
   - **Open Fees**: Total fees paid to open
3. Optional fields for closing:
   - **Close Date**: Date position was closed
   - **Assigned**: Yes/No if shares were assigned/called away
   - **Premium Paid to Close**: Amount paid to buy back
   - **Close Fees**: Fees paid to close
4. Add any notes about the trade

### Updating Option Prices

- Click the refresh icon next to any open position to fetch its current price
- Click "Refresh All Prices" in the summary section to update all open positions
- Prices are fetched from Yahoo Finance (delayed data)

### Viewing Metrics

- The main table shows key metrics for each position
- Expand rows (if they have notes or additional data) to see more details
- The Summary section at the top shows portfolio-wide statistics

### Filtering Positions

Use the filter section to:
- Search by stock ticker
- Filter by option type (Put/Call)
- View only open or closed positions

### Editing/Deleting Positions

- Click the edit icon to modify a position
- Click the delete icon to remove a position (confirmation required)

## API Endpoints

### Positions
- `GET /api/positions/` - List all positions
- `POST /api/positions/` - Create new position
- `GET /api/positions/{id}/` - Get specific position
- `PUT /api/positions/{id}/` - Update position
- `DELETE /api/positions/{id}/` - Delete position

### Custom Actions
- `GET /api/positions/summary/` - Get portfolio summary
- `GET /api/positions/by_stock/?stock=AAPL` - Get positions for specific stock
- `POST /api/positions/{id}/fetch_current_price/` - Fetch price for one position
- `POST /api/positions/fetch_all_current_prices/` - Fetch prices for all open positions

## Django Admin

Access the Django admin at `http://localhost:8000/admin/` to:
- View all positions in a table format
- Bulk edit positions
- See calculated fields
- Filter and search positions

## Notes

- All calculations are based on the formulas you specified for wheel strategy tracking
- Premium values are per contract (multiply by 100 for actual dollars)
- Fees should be entered as total amounts (not per contract)
- Date validation ensures close dates are after open dates
- Yahoo Finance data may be delayed and not always available for all strikes/expirations

## Future Enhancements

Potential features to add:
- Export positions to CSV/Excel
- Charts and graphs for performance over time
- Advanced analytics (win rate, best performing stocks, etc.)
- Multi-user support with authentication
- Mobile-responsive design improvements
- Real-time price updates via WebSocket
- Tax reporting features
