from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from .models import CreditSpread
from .serializers import CreditSpreadSerializer


class CreditSpreadViewSet(viewsets.ModelViewSet):
    """ViewSet for CreditSpread CRUD operations"""
    serializer_class = CreditSpreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter spreads by current user"""
        return CreditSpread.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for credit spreads"""
        spreads = self.get_queryset()

        # Open spreads
        open_spreads = spreads.filter(close_date__isnull=True)
        open_count = open_spreads.count()

        # Closed spreads
        closed_spreads = spreads.filter(close_date__isnull=False)
        closed_count = closed_spreads.count()

        # Calculate total net credit for open positions
        total_open_credit = sum(
            spread.net_credit for spread in open_spreads
        ) if open_count > 0 else Decimal('0.00')

        # Calculate total max risk for open positions
        total_open_risk = sum(
            spread.max_risk for spread in open_spreads
        ) if open_count > 0 else Decimal('0.00')

        # Calculate total P/L for closed positions
        total_closed_pl = sum(
            spread.profit_loss for spread in closed_spreads if spread.profit_loss is not None
        ) if closed_count > 0 else Decimal('0.00')

        # Calculate win rate (profitable closed spreads / total closed spreads)
        winning_spreads = sum(
            1 for spread in closed_spreads if spread.profit_loss and spread.profit_loss > 0
        )
        win_rate = (winning_spreads / closed_count * 100) if closed_count > 0 else 0

        # Calculate average days in trade for closed positions
        avg_days = sum(
            spread.days_in_trade for spread in closed_spreads
        ) / closed_count if closed_count > 0 else 0

        # Calculate average ROI for closed positions
        closed_rois = [
            spread.roi_percentage for spread in closed_spreads
            if spread.roi_percentage is not None
        ]
        avg_roi = sum(closed_rois) / len(closed_rois) if closed_rois else 0

        return Response({
            'total_spreads': spreads.count(),
            'open_spreads': open_count,
            'closed_spreads': closed_count,
            'total_open_credit': float(total_open_credit),
            'total_open_risk': float(total_open_risk),
            'total_closed_pl': float(total_closed_pl),
            'win_rate': float(win_rate),
            'avg_days_in_trade': float(avg_days),
            'avg_roi': float(avg_roi),
            'winning_spreads': winning_spreads,
        })

    @action(detail=False, methods=['get'])
    def by_stock(self, request):
        """Get spreads grouped by stock"""
        stock = request.query_params.get('stock')
        spreads = self.get_queryset()

        if stock:
            spreads = spreads.filter(stock__iexact=stock)

        # Group by stock and calculate stats
        stocks = {}
        for spread in spreads:
            if spread.stock not in stocks:
                stocks[spread.stock] = {
                    'stock': spread.stock,
                    'open_count': 0,
                    'closed_count': 0,
                    'total_credit': Decimal('0.00'),
                    'total_pl': Decimal('0.00'),
                }

            if spread.is_open:
                stocks[spread.stock]['open_count'] += 1
                stocks[spread.stock]['total_credit'] += spread.net_credit
            else:
                stocks[spread.stock]['closed_count'] += 1
                if spread.profit_loss:
                    stocks[spread.stock]['total_pl'] += spread.profit_loss

        # Convert to list and format decimals
        result = [
            {
                **stock_data,
                'total_credit': float(stock_data['total_credit']),
                'total_pl': float(stock_data['total_pl']),
            }
            for stock_data in stocks.values()
        ]

        return Response(result)
