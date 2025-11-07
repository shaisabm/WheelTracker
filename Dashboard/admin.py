from django.contrib import admin
from .models import Position, Feedback, Notification


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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'type', 'user', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('subject', 'description', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'user')

    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'type', 'subject', 'description')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Don't allow creating feedback from admin
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'user_display', 'is_read', 'created_by', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'read_at', 'created_by')

    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        """Display user or 'All Users' if null"""
        return obj.user.username if obj.user else 'All Users'
    user_display.short_description = 'Recipient'

    def save_model(self, request, obj, form, change):
        """Set created_by to current admin user"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
