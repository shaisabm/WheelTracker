from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from .models import Position, Feedback, Notification
from .serializers import PositionSerializer, PositionSummarySerializer, FeedbackSerializer, NotificationSerializer, NotificationCreateSerializer
from django.contrib.auth.models import User
import yfinance as yf
import logging
from decimal import Decimal
from Dashboard.utils import auto_close_expired_positions

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint"""
    return Response({'status': 'ok', 'message': 'Django is running'})



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
        """
        Filter positions by logged-in user.
        Also automatically close expired positions and reopen extended positions.
        """

        # Run auto-close/reopen logic for this user's positions
        auto_close_expired_positions()

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


    # @action(detail=True, methods=['post'])
    # def fetch_current_price(self, request, pk=None):
    #     """
    #     Fetch current option price from Yahoo Finance for a specific position
    #     """
    #     position = self.get_object()
    #
    #     try:
    #         ticker = yf.Ticker(position.stock)
    #
    #         # Format expiration date for yfinance
    #         exp_date = position.expiration.strftime('%Y-%m-%d')
    #
    #         # Get options chain for the expiration date
    #         try:
    #             options = ticker.option_chain(exp_date)
    #         except Exception as e:
    #             return Response(
    #                 {'error': f'No options data available for {position.stock} expiring {exp_date}'},
    #                 status=status.HTTP_404_NOT_FOUND
    #             )
    #
    #         # Get the appropriate chain based on option type
    #         if position.type == 'P':
    #             chain = options.puts
    #         else:
    #             chain = options.calls
    #
    #         # Find the option with matching strike
    #         strike_float = float(position.strike)
    #         matching_options = chain[chain['strike'] == strike_float]
    #
    #         if matching_options.empty:
    #             return Response(
    #                 {'error': f'No option found with strike ${position.strike}'},
    #                 status=status.HTTP_404_NOT_FOUND
    #             )
    #
    #         # Get the mid price (average of bid and ask)
    #         option = matching_options.iloc[0]
    #         bid = option.get('bid', 0)
    #         ask = option.get('ask', 0)
    #
    #         if bid == 0 and ask == 0:
    #             # Try to use lastPrice if bid/ask not available
    #             mid_price = option.get('lastPrice', 0)
    #         else:
    #             mid_price = (bid + ask) / 2
    #
    #         # Update the position with the current price
    #         position.current_option_price = Decimal(str(round(mid_price, 2)))
    #         position.save()
    #
    #         serializer = self.get_serializer(position)
    #         return Response({
    #             'success': True,
    #             'current_option_price': position.current_option_price,
    #             'position': serializer.data
    #         })
    #
    #     except Exception as e:
    #         return Response(
    #             {'error': str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    # @action(detail=False, methods=['post'])
    # def fetch_all_current_prices(self, request):
    #     """
    #     Fetch current option prices for all open positions
    #     """
    #     open_positions = Position.objects.filter(close_date__isnull=True)
    #     updated_count = 0
    #     errors = []
    #
    #     for position in open_positions:
    #         try:
    #             ticker = yf.Ticker(position.stock)
    #             exp_date = position.expiration.strftime('%Y-%m-%d')
    #
    #             options = ticker.option_chain(exp_date)
    #             chain = options.puts if position.type == 'P' else options.calls
    #
    #             strike_float = float(position.strike)
    #             matching_options = chain[chain['strike'] == strike_float]
    #
    #             if not matching_options.empty:
    #                 option = matching_options.iloc[0]
    #                 bid = option.get('bid', 0)
    #                 ask = option.get('ask', 0)
    #
    #                 if bid == 0 and ask == 0:
    #                     mid_price = option.get('lastPrice', 0)
    #                 else:
    #                     mid_price = (bid + ask) / 2
    #
    #                 position.current_option_price = Decimal(str(round(mid_price, 2)))
    #                 position.save()
    #                 updated_count += 1
    #
    #         except Exception as e:
    #             errors.append({
    #                 'position_id': position.id,
    #                 'stock': position.stock,
    #                 'error': str(e)
    #             })
    #
    #     return Response({
    #         'success': True,
    #         'updated_count': updated_count,
    #         'total_open_positions': open_positions.count(),
    #         'errors': errors
    #     })

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

        # Calculate total realized P/L for closed positions
        closed_pos = positions.filter(close_date__isnull=False)
        realized_pl = Decimal('0.00')
        for pos in closed_pos:
            if pos.profit_loss:
                realized_pl += pos.profit_loss

        # Calculate total unrealized P/L for open positions
        open_pos = positions.filter(close_date__isnull=True)
        unrealized_pl = Decimal('0.00')
        for pos in open_pos:
            # Calculate unrealized P/L: premium collected - current value - fees
            premium_collected = pos.premium * pos.num_contracts * 100
            open_fees = pos.open_fees or Decimal('0.00')

            if pos.current_option_price is not None:
                # If we have current price, estimate P/L
                current_value = pos.current_option_price * pos.num_contracts * 100
                estimated_close_fees = open_fees  # Estimate close fees same as open
                unrealized_pl += premium_collected - current_value - open_fees - estimated_close_fees
            else:
                # If no current price, just count premium minus open fees
                unrealized_pl += premium_collected - open_fees

        # Calculate total collateral at risk for open positions
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
            'realized_pl': realized_pl,
            'unrealized_pl': unrealized_pl,
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


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user feedback, bug reports, and feature requests.
    Regular users can create feedback. Only admins can view all feedback.
    """
    serializer_class = FeedbackSerializer
    filterset_fields = ['type', 'status']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'type', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Admin users can see all feedback.
        Regular users can only see their own feedback.
        """
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)

    def get_permissions(self):
        """
        Admin users can list, retrieve, update, and delete feedback.
        Authenticated users can create feedback.
        """
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            # Require authentication for creating feedback
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Automatically assign the logged-in user to new feedback"""
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter notifications by current user"""
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def send_notification(self, request):
        """Send notification to users (admin only)"""
        try:
            serializer = NotificationCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_ids = serializer.validated_data.get('user_ids', [])
            notification_type = serializer.validated_data['type']
            title = serializer.validated_data['title']
            message = serializer.validated_data['message']

            if user_ids:
                # Send to specific users
                # Verify all user IDs exist first
                existing_user_ids = list(User.objects.filter(id__in=user_ids).values_list('id', flat=True))
                if len(existing_user_ids) != len(user_ids):
                    missing_ids = set(user_ids) - set(existing_user_ids)
                    logger.error(f"User IDs do not exist: {missing_ids}")
                    return Response({
                        'error': f'Some user IDs do not exist: {missing_ids}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                notifications = [
                    Notification(
                        user_id=user_id,
                        type=notification_type,
                        title=title,
                        message=message,
                        created_by=request.user
                    ) for user_id in existing_user_ids
                ]
            else:
                # Send to all users
                users = list(User.objects.all())
                if not users:
                    logger.warning("No users found in the system")
                    return Response({
                        'error': 'No users found in the system'
                    }, status=status.HTTP_400_BAD_REQUEST)

                notifications = [
                    Notification(
                        user=user,
                        type=notification_type,
                        title=title,
                        message=message,
                        created_by=request.user
                    ) for user in users
                ]

            # Bulk create notifications
            try:
                created_notifications = Notification.objects.bulk_create(notifications)
                logger.info(f"Successfully created {len(created_notifications)} notifications")
                return Response({
                    'success': True,
                    'message': f'Notification sent to {len(created_notifications)} user(s)',
                    'count': len(created_notifications)
                }, status=status.HTTP_201_CREATED)
            except Exception as db_error:
                logger.error(f"Database error during bulk_create: {str(db_error)}", exc_info=True)
                return Response({
                    'error': f'Database error: {str(db_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}", exc_info=True)
            return Response({
                'error': f'Failed to send notification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for current user"""
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'success': True,
            'message': f'Marked {updated} notification(s) as read',
            'count': updated
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def users_list(self, request):
        """Get list of all users for admin to send notifications"""
        users = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name')
        return Response(list(users))
