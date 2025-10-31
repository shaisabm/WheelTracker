from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from decimal import Decimal
from .models import Position
from .serializers import PositionSerializer, PositionSummarySerializer
import yfinance as yf



class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wheel strategy positions.
    Provides CRUD operations plus custom actions for fetching option prices and summaries.
    """
    serializer_class = PositionSerializer
    filterset_fields = ['stock', 'type', 'assigned']
    search_fields = ['stock', 'notes']
    ordering_fields = ['open_date', 'expiration', 'stock', 'profit_loss']
    ordering = ['-open_date']

    def get_queryset(self):
        """Filter positions by logged-in user"""
        return Position.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the logged-in user to new positions"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to provide better error logging"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
            print(f"Request data: {request.data}")
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def fetch_current_price(self, request, pk=None):
        """
        Fetch current option price from Yahoo Finance for a specific position
        """
        position = self.get_object()

        try:
            ticker = yf.Ticker(position.stock)

            # Format expiration date for yfinance
            exp_date = position.expiration.strftime('%Y-%m-%d')

            # Get options chain for the expiration date
            try:
                options = ticker.option_chain(exp_date)
            except Exception as e:
                return Response(
                    {'error': f'No options data available for {position.stock} expiring {exp_date}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the appropriate chain based on option type
            if position.type == 'P':
                chain = options.puts
            else:
                chain = options.calls

            # Find the option with matching strike
            strike_float = float(position.strike)
            matching_options = chain[chain['strike'] == strike_float]

            if matching_options.empty:
                return Response(
                    {'error': f'No option found with strike ${position.strike}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the mid price (average of bid and ask)
            option = matching_options.iloc[0]
            bid = option.get('bid', 0)
            ask = option.get('ask', 0)

            if bid == 0 and ask == 0:
                # Try to use lastPrice if bid/ask not available
                mid_price = option.get('lastPrice', 0)
            else:
                mid_price = (bid + ask) / 2

            # Update the position with the current price
            position.current_option_price = Decimal(str(round(mid_price, 2)))
            position.save()

            serializer = self.get_serializer(position)
            return Response({
                'success': True,
                'current_option_price': position.current_option_price,
                'position': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def fetch_all_current_prices(self, request):
        """
        Fetch current option prices for all open positions
        """
        open_positions = Position.objects.filter(close_date__isnull=True)
        updated_count = 0
        errors = []

        for position in open_positions:
            try:
                ticker = yf.Ticker(position.stock)
                exp_date = position.expiration.strftime('%Y-%m-%d')

                options = ticker.option_chain(exp_date)
                chain = options.puts if position.type == 'P' else options.calls

                strike_float = float(position.strike)
                matching_options = chain[chain['strike'] == strike_float]

                if not matching_options.empty:
                    option = matching_options.iloc[0]
                    bid = option.get('bid', 0)
                    ask = option.get('ask', 0)

                    if bid == 0 and ask == 0:
                        mid_price = option.get('lastPrice', 0)
                    else:
                        mid_price = (bid + ask) / 2

                    position.current_option_price = Decimal(str(round(mid_price, 2)))
                    position.save()
                    updated_count += 1

            except Exception as e:
                errors.append({
                    'position_id': position.id,
                    'stock': position.stock,
                    'error': str(e)
                })

        return Response({
            'success': True,
            'updated_count': updated_count,
            'total_open_positions': open_positions.count(),
            'errors': errors
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary statistics for all positions for the logged-in user
        """
        positions = Position.objects.filter(user=request.user)

        # Calculate metrics
        total_positions = positions.count()
        open_positions = positions.filter(close_date__isnull=True).count()
        closed_positions = positions.filter(close_date__isnull=False).count()

        # Calculate total P/L for closed positions
        closed_pos = positions.filter(close_date__isnull=False)
        total_pl = Decimal('0.00')
        for pos in closed_pos:
            if pos.profit_loss:
                total_pl += pos.profit_loss

        # Calculate total premium collected (premium per contract × num contracts × 100)
        total_premium_dollars = Decimal('0.00')
        for pos in positions:
            total_premium_dollars += pos.premium * pos.num_contracts * 100

        # Calculate total collateral at risk for open positions
        open_pos = positions.filter(close_date__isnull=True)
        total_collateral = Decimal('0.00')
        for pos in open_pos:
            total_collateral += pos.collateral_requirement

        # Calculate average AR for closed trades
        closed_with_ar = [pos for pos in closed_pos if pos.ar_of_closed_trade is not None]
        avg_ar = None
        if closed_with_ar:
            avg_ar = sum(pos.ar_of_closed_trade for pos in closed_with_ar) / len(closed_with_ar)

        # Get list of stocks traded
        stocks = list(positions.values_list('stock', flat=True).distinct().order_by('stock'))

        summary_data = {
            'total_positions': total_positions,
            'open_positions': open_positions,
            'closed_positions': closed_positions,
            'total_profit_loss': total_pl,
            'total_premium_collected': total_premium_dollars,
            'total_collateral_at_risk': total_collateral,
            'average_ar_closed_trades': avg_ar,
            'stocks_traded': stocks
        }

        serializer = PositionSummarySerializer(summary_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_stock(self, request):
        """
        Get positions grouped by stock
        """
        stock = request.query_params.get('stock')
        if stock:
            positions = Position.objects.filter(stock=stock.upper())
            serializer = self.get_serializer(positions, many=True)
            return Response(serializer.data)

        # Return all stocks with position counts
        stocks = Position.objects.values('stock').annotate(
            count=Count('id'),
            open_count=Count('id', filter=Q(close_date__isnull=True)),
            closed_count=Count('id', filter=Q(close_date__isnull=False))
        ).order_by('stock')

        return Response(stocks)

    @action(detail=False, methods=['get'])
    def roi_summary(self, request):
        """
        Get ROI summary for a date range
        Only includes CLOSED positions (realized gains)
        Query params: start_date, end_date (YYYY-MM-DD format, optional)
        """
        from datetime import datetime

        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Start with closed positions only for the logged-in user
        positions = Position.objects.filter(user=request.user, close_date__isnull=False)

        # Apply date filters if provided (using open_date)
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                positions = positions.filter(open_date__gte=start)
            except ValueError:
                return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD'}, status=400)

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                positions = positions.filter(open_date__lte=end)
            except ValueError:
                return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD'}, status=400)

        # Calculate totals
        total_premium = Decimal('0.00')
        total_collateral = Decimal('0.00')
        position_count = 0

        for pos in positions:
            # Use profit_loss which accounts for premium collected, premium paid to close, and all fees
            profit = pos.profit_loss
            collateral = pos.collateral_requirement

            total_premium += profit
            total_collateral += collateral
            position_count += 1

        # Calculate ROI
        roi_percentage = None
        if total_collateral > 0:
            roi_percentage = (total_premium / total_collateral * 100)

        return Response({
            'premium': total_premium,
            'collateral': total_collateral,
            'roi_percentage': roi_percentage,
            'position_count': position_count,
            'start_date': start_date,
            'end_date': end_date
        })
