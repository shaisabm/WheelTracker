from django.contrib import admin
from .models import CreditSpread


@admin.register(CreditSpread)
class CreditSpreadAdmin(admin.ModelAdmin):
    list_display = [
        'stock',
        'type',
        'short_strike',
        'long_strike',
        'open_date',
        'expiration',
        'num_contracts',
        'net_credit',
        'is_open',
        'user',
    ]
    list_filter = ['type', 'stock', 'open_date']
    search_fields = ['stock', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'net_credit',
        'max_risk',
        'max_profit',
        'profit_loss',
        'roi_percentage',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'stock', 'type', 'open_date', 'expiration', 'num_contracts')
        }),
        ('Long Leg (Bought)', {
            'fields': ('long_strike', 'long_premium')
        }),
        ('Short Leg (Sold)', {
            'fields': ('short_strike', 'short_premium')
        }),
        ('Fees', {
            'fields': ('open_fees', 'close_fees')
        }),
        ('Closing Information', {
            'fields': ('close_date', 'long_close_premium', 'short_close_premium')
        }),
        ('Current Pricing', {
            'fields': ('current_long_price', 'current_short_price')
        }),
        ('Calculated Fields', {
            'fields': ('net_credit', 'max_risk', 'max_profit', 'profit_loss', 'roi_percentage'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
