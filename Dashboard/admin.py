from django.contrib import admin
from .models import Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'wheel_cycle_name', 'type', 'strike', 'open_date', 'expiration', 'is_open', 'profit_loss')
    list_filter = ('type', 'stock', 'assigned', 'open_date')
    search_fields = ('stock', 'notes', 'wheel_cycle_name')
    date_hierarchy = 'open_date'
    readonly_fields = ('created_at', 'updated_at', 'profit_loss', 'ar_if_held_to_expiration', 'ar_of_closed_trade', 'wheel_cycle_number', 'is_wheel_complete')

    fieldsets = (
        ('Basic Information', {
            'fields': ('open_date', 'stock', 'type')
        }),
        ('Wheel Cycle Tracking', {
            'fields': ('wheel_cycle_name', 'related_to'),
            'description': 'Link positions together to track a complete wheel cycle'
        }),
        ('Contract Details', {
            'fields': ('expiration', 'num_contracts', 'strike', 'premium')
        }),
        ('Opening Transaction', {
            'fields': ('open_fees',)
        }),
        ('Closing Transaction', {
            'fields': ('close_date', 'assigned', 'premium_paid_to_close', 'close_fees')
        }),
        ('Market Data', {
            'fields': ('current_option_price',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Calculated Fields', {
            'fields': ('profit_loss', 'ar_if_held_to_expiration', 'ar_of_closed_trade'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
