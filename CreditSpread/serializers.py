from rest_framework import serializers
from .models import CreditSpread


class CreditSpreadSerializer(serializers.ModelSerializer):
    # Read-only computed fields
    is_open = serializers.ReadOnlyField()
    days_in_trade = serializers.ReadOnlyField()
    days_to_expiration = serializers.ReadOnlyField()
    original_dte = serializers.ReadOnlyField()
    net_credit = serializers.ReadOnlyField()
    max_risk = serializers.ReadOnlyField()
    max_profit = serializers.ReadOnlyField()
    profit_loss = serializers.ReadOnlyField()
    roi_percentage = serializers.ReadOnlyField()
    ar_if_held_to_expiration = serializers.ReadOnlyField()
    ar_of_closed_trade = serializers.ReadOnlyField()
    current_profit_loss = serializers.ReadOnlyField()
    break_even_price = serializers.ReadOnlyField()

    class Meta:
        model = CreditSpread
        fields = [
            'id',
            'user',
            'open_date',
            'stock',
            'expiration',
            'type',
            'long_strike',
            'long_premium',
            'short_strike',
            'short_premium',
            'num_contracts',
            'open_fees',
            'close_date',
            'long_close_premium',
            'short_close_premium',
            'close_fees',
            'notes',
            'current_long_price',
            'current_short_price',
            'created_at',
            'updated_at',
            # Computed fields
            'is_open',
            'days_in_trade',
            'days_to_expiration',
            'original_dte',
            'net_credit',
            'max_risk',
            'max_profit',
            'profit_loss',
            'roi_percentage',
            'ar_if_held_to_expiration',
            'ar_of_closed_trade',
            'current_profit_loss',
            'break_even_price',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)