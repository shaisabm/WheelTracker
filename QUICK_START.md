# Quick Start Guide - Wheel Strategy Tracker

## What You Have

A complete, professional dashboard for tracking options trading with the wheel strategy:

### Backend (Django)
- ✅ Django REST API with full CRUD operations
- ✅ Position model with all required fields
- ✅ Automatic calculation of P/L, AR%, and other metrics
- ✅ Yahoo Finance integration for live option prices
- ✅ Django admin interface
- ✅ CORS configured for frontend communication

### Frontend (Svelte)
- ✅ Modern, responsive dashboard with Tailwind CSS
- ✅ Position input form with validation
- ✅ Comprehensive position table with all metrics
- ✅ Portfolio summary with key statistics
- ✅ Filtering by stock, type, and status
- ✅ Real-time option price fetching
- ✅ Edit and delete functionality

### Features Implemented
- ✅ All input fields you specified (Open Date, Stock, Set, Expiration, Type, etc.)
- ✅ All calculated fields (Profit/Loss, AR%, Set Break Even, etc.)
- ✅ Yahoo Finance price integration
- ✅ Sample data creation script
- ✅ Complete documentation

## Starting the Application

### Option 1: Using the startup script (recommended)
```bash
./start_dev.sh
```

### Option 2: Manual start

**Terminal 1 - Backend:**
```bash
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access Points

Once started, you can access:
- **Dashboard:** http://localhost:5173/
- **API:** http://localhost:8000/api/positions/
- **Django Admin:** http://localhost:8000/admin/

## First Steps

1. **Start the servers** (see above)

2. **Load sample data** (optional):
   ```bash
   python create_sample_data.py
   ```

3. **Open the dashboard** at http://localhost:5173/

4. **Try these actions:**
   - View the portfolio summary at the top
   - Browse existing positions in the table
   - Click "+ New Position" to add a position
   - Use filters to search by stock, type, or status
   - Click the refresh icon to fetch current option prices
   - Edit or delete positions using the action buttons

## Key Files

### Backend
- `Dashboard/models.py` - Position model with all calculated properties
- `Dashboard/views.py` - API views and custom actions
- `Dashboard/serializers.py` - Data serialization
- `Dashboard/admin.py` - Django admin configuration

### Frontend
- `frontend/src/routes/+page.svelte` - Main dashboard page
- `frontend/src/lib/components/PositionForm.svelte` - Input form
- `frontend/src/lib/components/PositionTable.svelte` - Position list
- `frontend/src/lib/components/Summary.svelte` - Portfolio summary
- `frontend/src/lib/api.js` - API client

### Documentation
- `README.md` - Complete project documentation
- `FORMULAS.md` - Detailed formula reference
- `QUICK_START.md` - This file

## Adding Your First Real Position

1. Click "+ New Position"
2. Fill in the required fields (marked with *):
   - **Open Date**: Today's date or when you opened the trade
   - **Stock**: Ticker symbol (e.g., AAPL)
   - **Expiration**: Contract expiration date
   - **Type**: P for Put, C for Call
   - **# Contracts**: How many contracts
   - **Strike**: Strike price
   - **Premium**: Premium per contract you received
3. Optional but recommended:
   - **Open Fees**: Total fees paid to open
   - **Set Number**: Use 1 for your first wheel cycle with this stock
   - **Notes**: Any notes about the trade
4. Click "Create Position"

## Closing a Position

1. Find the position in the table
2. Click the edit icon (pencil)
3. Fill in the closing information:
   - **Close Date**: Date you closed it
   - **Assigned**: Yes if shares were assigned/called away
   - **Premium Paid to Close**: Amount you paid (0 if held to expiration)
   - **Close Fees**: Fees paid to close
4. Click "Update Position"

The P/L and actual AR% will be automatically calculated!

## Fetching Current Prices

### For a single position:
Click the refresh icon (↻) next to the Current Price column

### For all open positions:
Click "Refresh All Prices" button in the Summary section

**Note:** Yahoo Finance data may be delayed. Prices are fetched as the mid-point between bid and ask.

## Understanding the Metrics

### Open Positions Show:
- **AR% if Held to Expiration**: Annualized return if you hold through expiration
- **AR% on Realized Premium**: What you'd get if you closed at current price
- **AR% on Remaining Premium**: Return on remaining value until expiration
- **% Premium Earned**: How much of the premium you've captured

### Closed Positions Show:
- **Profit/Loss**: Net P/L after all premiums and fees
- **AR% of Closed Trade**: Actual annualized return achieved
- **Days in Trade**: How long you held the position

See `FORMULAS.md` for detailed calculation explanations.

## Tips for Wheel Strategy Tracking

1. **Use Set Numbers**: Track different wheel cycles for the same stock
   - Sell put (Set 1) → Get assigned → Sell call (Set 1) → Called away
   - Next time you trade that stock, use Set 2

2. **Track Rolls**: When rolling positions:
   - Close the old position (enter close data)
   - Create a new position for the rolled contract
   - Use the same Set Number
   - Add notes explaining the roll

3. **Monitor AR%**:
   - Use "AR% on Remaining Premium" to decide if you should close early
   - Compare against other opportunities
   - If remaining AR% is low, consider rolling to a new position

4. **Use Filters**:
   - Filter by stock to see all wheels for one ticker
   - Filter by "Open" to focus on active management
   - Filter by "Closed" to analyze past performance

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Ensure you're in the project root directory
- Check migrations are applied: `python manage.py migrate`

### Frontend won't start
- Check if port 5173 is already in use: `lsof -i :5173`
- Ensure you're in the frontend directory
- Try reinstalling dependencies: `npm install`

### Can't fetch prices
- Check your internet connection
- Verify the stock ticker is correct
- Ensure the expiration date has options available
- Yahoo Finance may not have all strikes/expirations

### CORS errors
- Make sure Django server is running on port 8000
- Check CORS settings in `WheelTracker/settings.py`
- Frontend should be on port 5173

## Next Steps

1. **Create a superuser** to access Django admin:
   ```bash
   python manage.py createsuperuser
   ```

2. **Explore the Django Admin** at http://localhost:8000/admin/
   - View all positions in a table
   - Bulk edit positions
   - See calculated fields

3. **Customize the dashboard**:
   - Adjust colors in the Svelte components
   - Add additional calculated fields in `models.py`
   - Create custom reports in the API

4. **Export data** (future enhancement):
   - Currently, you can view data through Django admin
   - Consider adding CSV export functionality
   - Create custom reports for tax purposes

## Need Help?

- Check `README.md` for detailed documentation
- Review `FORMULAS.md` for calculation details
- Examine `create_sample_data.py` to see data structure
- Look at existing sample positions for examples

## What's Not Included (Future Enhancements)

- Real-time price updates (currently manual refresh)
- Charts and graphs
- Multi-user authentication
- CSV/Excel export
- Advanced analytics (win rate, best stocks, etc.)
- Mobile app
- Tax reporting features
- Automated trade import from brokers

The foundation is solid and ready for these additions!
