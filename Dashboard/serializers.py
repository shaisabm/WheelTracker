from rest_framework import serializers
from .models import Position, Feedback, Notification
from decimal import Decimal
from django.contrib.auth.models import User


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for Position model with calculated fields"""

    # Wheel cycle fields
    wheel_cycle_number = serializers.IntegerField(read_only=True)
    is_wheel_complete = serializers.BooleanField(read_only=True)

    # Calculated read-only fields
    profit_loss = serializers.DecimalField(
        max_digits=10, decimal_places=3, read_only=True
    )
    ar_if_held_to_expiration = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    ar_of_closed_trade = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    ar_on_realized_premium = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    ar_on_remaining_premium = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    percent_premium_earned = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    set_break_even_price_puts = serializers.DecimalField(
        max_digits=10, decimal_places=3, read_only=True, allow_null=True
    )
    is_open = serializers.BooleanField(read_only=True)
    days_in_trade = serializers.IntegerField(read_only=True)
    days_to_expiration = serializers.IntegerField(read_only=True)
    days_open_to_expiration = serializers.IntegerField(read_only=True)
    collateral_requirement = serializers.DecimalField(
        max_digits=10, decimal_places=3, read_only=True
    )
    roi_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )

    class Meta:
        model = Position
        fields = [
            'id',
            'open_date',
            'stock',
            'related_to',
            'wheel_cycle_name',
            'wheel_cycle_number',
            'is_wheel_complete',
            'expiration',
            'type',
            'num_contracts',
            'strike',
            'premium',
            'open_fees',
            'close_date',
            'assigned',
            'premium_paid_to_close',
            'close_fees',
            'notes',
            'created_at',
            'updated_at',
            # Calculated fields
            'is_open',
            'days_in_trade',
            'days_to_expiration',
            'days_open_to_expiration',
            'profit_loss',
            'collateral_requirement',
            'ar_if_held_to_expiration',
            'ar_of_closed_trade',
            'ar_on_realized_premium',
            'ar_on_remaining_premium',
            'percent_premium_earned',
            'set_break_even_price_puts',
            'roi_percentage',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validate position data"""
        # If close_date is provided, ensure premium_paid_to_close is also provided
        if data.get('close_date') and data.get('premium_paid_to_close') is None:
            raise serializers.ValidationError(
                "premium_paid_to_close is required when close_date is provided"
            )

        # Validate expiration is after open_date
        if data.get('open_date') and data.get('expiration'):
            if data['expiration'] < data['open_date']:
                raise serializers.ValidationError(
                    "Expiration date must be after open date"
                )

        # Validate close_date is after open_date
        if data.get('open_date') and data.get('close_date'):
            if data['close_date'] < data['open_date']:
                raise serializers.ValidationError(
                    "Close date must be after open date"
                )

        return data


class PositionSummarySerializer(serializers.Serializer):
    """Serializer for position summary statistics"""
    total_positions = serializers.IntegerField()
    open_positions = serializers.IntegerField()
    closed_positions = serializers.IntegerField()
    realized_pl = serializers.DecimalField(max_digits=12, decimal_places=2)
    unrealized_pl = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_collateral_at_risk = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_ar_closed_trades = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    stocks_traded = serializers.ListField(child=serializers.CharField())


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id',
            'type',
            'subject',
            'description',
            'status',
            'created_at',
            'updated_at',
            'username',
        ]
        read_only_fields = ['created_at', 'updated_at', 'username']

    def validate(self, data):
        """Validate feedback data"""
        # Only validate required fields on creation, not on partial updates
        if not self.partial:
            if not data.get('subject') or not data.get('subject').strip():
                raise serializers.ValidationError("Subject is required")

            if not data.get('description') or not data.get('description').strip():
                raise serializers.ValidationError("Description is required")

        return data


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""

    username = serializers.CharField(source='user.username', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'username',
            'type',
            'title',
            'message',
            'is_read',
            'created_by',
            'created_by_username',
            'created_at',
            'read_at',
        ]
        read_only_fields = ['created_at', 'read_at', 'created_by']


class NotificationCreateSerializer(serializers.Serializer):
    """Serializer for creating notifications"""

    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of user IDs to send notification to. Leave empty for all users."
    )
    type = serializers.ChoiceField(
        choices=Notification.TYPE_CHOICES,
        default='info'
    )
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()

    def validate_user_ids(self, value):
        """Validate that all user IDs exist"""
        if value:
            existing_users = User.objects.filter(id__in=value).count()
            if existing_users != len(value):
                raise serializers.ValidationError("Some user IDs do not exist")
        return value
