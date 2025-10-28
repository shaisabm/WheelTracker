from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from decimal import Decimal
from .models import Position
from .serializers import PositionSerializer, PositionSummarySerializer
import yfinance as yf
from datetime import datetime


class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wheel strategy positions.
    Provides CRUD operations plus custom actions for fetching option prices and summaries.
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filterset_fields = ['stock', 'type', 'set_number', 'assigned']
    search_fields = ['stock', 'notes']
    ordering_fields = ['open_date', 'expiration', 'stock', 'profit_loss']
    ordering = ['-open_date']

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
        Get summary statistics for all positions
        """
        positions = Position.objects.all()

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

        # Calculate total premium collected
        total_premium = positions.aggregate(
            total=Sum('premium')
        )['total'] or Decimal('0.00')
        total_premium_dollars = total_premium * 100  # Convert to dollars

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
