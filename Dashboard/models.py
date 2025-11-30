from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime
import pytz


class Position(models.Model):
    """Model for tracking wheel strategy option positions"""

    TYPE_CHOICES = [
        ('P', 'Put'),
        ('C', 'Call'),
    ]

    ASSIGNED_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    # User association
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions', null=True)

    # User input fields
    open_date = models.DateField(help_text="The date that you open the contract")
    stock = models.CharField(max_length=10, help_text="The ticker of the contract's underlying position")
    related_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_positions',
        help_text="Link to previous position in the wheel cycle (e.g., link a covered call to the put that got assigned)"
    )
    wheel_cycle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional name for this wheel cycle (e.g., 'AAPL Jan 2025', 'TSLA Wheel #1')"
    )
    expiration = models.DateField(help_text="The expiration date of the contract")
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, help_text="P for Put or C for Call")
    num_contracts = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="The number of contracts"
    )
    strike = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="The strike price for the contract"
    )
    premium = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The amount of premium received for selling your call or put"
    )
    open_fees = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Commissions and fees paid to open a trade (total for all contracts)"
    )
    close_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date you close a position (or expiration date if held through expiration)"
    )
    assigned = models.CharField(
        max_length=3,
        choices=ASSIGNED_CHOICES,
        default='No',
        help_text="Enter Yes if assigned shares or had shares called away, otherwise No"
    )
    premium_paid_to_close = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The amount paid to close the position (0 if held through expiration)"
    )
    close_fees = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Commissions and fees paid to close a trade"
    )
    notes = models.TextField(
        blank=True,
        help_text="Any notes or comments about the contract"
    )
    entry_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The stock price when you entered the position"
    )

    # Calculated/fetched fields
    current_option_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The mid price the option is currently trading for (from Yahoo Finance)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-open_date']
        indexes = [
            models.Index(fields=['stock']),
            models.Index(fields=['open_date']),
            models.Index(fields=['expiration']),
            models.Index(fields=['wheel_cycle_name']),
        ]

    def __str__(self):
        cycle_info = f" ({self.wheel_cycle_name})" if self.wheel_cycle_name else ""
        return f"{self.stock}{cycle_info} - {self.get_type_display()} ${self.strike} exp {self.expiration}"

    def get_wheel_cycle_positions(self):
        """Get all positions in this wheel cycle (following the chain)"""
        positions = [self]

        # Follow the chain backwards
        current = self.related_to
        while current:
            positions.insert(0, current)
            current = current.related_to

        # Follow the chain forwards
        for related in self.related_positions.all():
            positions.extend(related.get_wheel_cycle_positions()[1:])  # Skip the current position

        return positions

    @property
    def wheel_cycle_number(self):
        """Calculate which position this is in the wheel cycle (1, 2, 3, etc.)"""
        cycle_positions = self.get_wheel_cycle_positions()
        try:
            return cycle_positions.index(self) + 1
        except ValueError:
            return 1

    @property
    def is_wheel_complete(self):
        """Check if this wheel cycle is complete (had assignment and shares called away)"""
        cycle_positions = self.get_wheel_cycle_positions()
        has_put_assignment = any(p.type == 'P' and p.assigned == 'Yes' for p in cycle_positions)
        has_call_assignment = any(p.type == 'C' and p.assigned == 'Yes' for p in cycle_positions)
        return has_put_assignment and has_call_assignment

    @property
    def is_open(self):
        """Check if the position is still open"""
        return self.close_date is None

    @property
    def days_in_trade(self):
        """Calculate the number of days the trade was held (using ET timezone)"""
        if self.close_date:
            return (self.close_date - self.open_date).days
        et_tz = pytz.timezone('US/Eastern')
        today_et = datetime.now(et_tz).date()
        return (today_et - self.open_date).days

    @property
    def days_to_expiration(self):
        """Calculate the number of days remaining until expiration (using ET timezone)"""
        if self.close_date:
            return 0
        et_tz = pytz.timezone('US/Eastern')
        today_et = datetime.now(et_tz).date()
        days = (self.expiration - today_et).days
        return max(0, days)

    @property
    def days_open_to_expiration(self):
        """Calculate total days from open to expiration"""
        return (self.expiration - self.open_date).days

    @property
    def profit_loss(self):
        """Calculate P/L: ((Premium received - Price paid to close) x # contracts) - total fees"""
        if self.close_date is None:
            return None

        premium_paid = self.premium_paid_to_close or Decimal('0.00')
        close_fees_val = self.close_fees or Decimal('0.00')

        gross_profit = (self.premium - premium_paid) * self.num_contracts * 100
        total_fees = self.open_fees + close_fees_val

        return gross_profit - total_fees

    @property
    def collateral_requirement(self):
        """Calculate the collateral requirement for the position"""
        # For cash-secured puts: strike * 100 * num_contracts
        # For covered calls: This would be 0 since you already own the shares
        if self.type == 'P':
            return self.strike * 100 * self.num_contracts
        return 0

    @property
    def risk_less_premium(self):
        """Calculate risk less premium collected on open"""
        premium_collected = (self.premium * self.num_contracts * 100) - self.open_fees
        return self.collateral_requirement - premium_collected

    @property
    def ar_if_held_to_expiration(self):
        """Calculate Annualized Rate of Return if held to expiration
        Formula: (365 / days_open_to_expiration) * (premium / collateral) * 100
        """
        if self.days_open_to_expiration == 0:
            return None

        premium_dollars = self.premium * self.num_contracts * 100

        # For covered calls, use the value of shares as collateral
        if self.type == 'C':
            collateral = self.strike * 100 * self.num_contracts
        else:
            collateral = self.collateral_requirement

        if collateral <= 0:
            return None

        return (Decimal('365') / self.days_open_to_expiration) * (premium_dollars / collateral) * 100

    @property
    def ar_of_closed_trade(self):
        """Calculate actual Annualized Rate of Return for closed trades
        Formula: (365 / days_in_trade) * (profit_loss / collateral) * 100
        """
        if self.close_date is None or self.days_in_trade == 0:
            return None

        pl = self.profit_loss
        if pl is None:
            return None

        # For covered calls, use the value of shares as collateral
        if self.type == 'C':
            collateral = self.strike * 100 * self.num_contracts
        else:
            collateral = self.collateral_requirement

        if collateral <= 0:
            return None

        return (Decimal('365') / self.days_in_trade) * (pl / collateral) * 100

    @property
    def ar_on_realized_premium(self):
        """Calculate AR on realized premium for open positions"""
        if self.close_date is not None or self.days_in_trade == 0:
            return None

        if self.current_option_price is None:
            return None

        # Realized P/L if closed at current price
        premium_paid = self.current_option_price
        close_fees_estimated = self.open_fees  # Estimate close fees same as open fees
        gross_profit = (self.premium - premium_paid) * self.num_contracts * 100
        realized_pl = gross_profit - self.open_fees - close_fees_estimated

        risk = self.risk_less_premium
        if risk <= 0:
            return None

        return (Decimal('365') * realized_pl / risk / self.days_in_trade) * 100

    @property
    def ar_on_remaining_premium(self):
        """Calculate AR on remaining premium for open positions"""
        if self.close_date is not None or self.days_to_expiration == 0:
            return None

        if self.current_option_price is None:
            return None

        # Cost to close
        cost_to_close = self.current_option_price * self.num_contracts * 100

        risk = self.risk_less_premium
        if risk <= 0:
            return None

        return (Decimal('365') * cost_to_close / risk / self.days_to_expiration) * 100

    @property
    def percent_premium_earned(self):
        """Calculate % of premium earned at current option price"""
        if self.current_option_price is None:
            return None

        if self.premium == 0:
            return None

        premium_earned = self.premium - self.current_option_price
        return (premium_earned / self.premium) * 100

    @property
    def set_break_even_price_puts(self):
        """
        Calculate break-even price for puts
        Formula: (strike price * (100 * number of contracts) - P/L) / (number of contracts * 100)
        """
        if self.type != 'P':
            return None

        # Only calculate for closed positions
        if not self.close_date:
            return None

        pl = self.profit_loss
        if pl is None:
            return None

        # Break Even = (Strike * Shares - P/L) / Shares
        total_shares = self.num_contracts * 100
        strike_value = self.strike * total_shares

        break_even = (strike_value - pl) / total_shares
        return break_even

    @property
    def roi_percentage(self):
        """
        Calculate ROI percentage: (premium / collateral) * 100
        This shows the return on investment for the position
        """
        collateral = self.collateral_requirement
        if not collateral or collateral == 0:
            return None

        # Premium collected in dollars
        premium_dollars = self.premium * self.num_contracts * 100

        # ROI = (Premium / Collateral) * 100
        roi = (premium_dollars / collateral) * 100
        return roi


class Feedback(models.Model):
    """Model for user feedback, bug reports, and feature requests"""

    TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ]

    # User who submitted the feedback
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')

    # Feedback details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, help_text="Type of feedback")
    subject = models.CharField(max_length=200, help_text="Brief summary of the feedback")
    description = models.TextField(help_text="Detailed description")

    # Status tracking (only visible to admin)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not visible to users)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject} (by {self.user.username})"


class Notification(models.Model):
    """Model for system notifications sent to users

    Each notification is sent to a specific user. To send to all users,
    individual notification records are created for each user via bulk_create.
    """

    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('announcement', 'Announcement'),
    ]

    # User who receives the notification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who receives this notification"
    )

    # Notification details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info', help_text="Type of notification")
    title = models.CharField(max_length=200, help_text="Notification title")
    message = models.TextField(help_text="Notification message")

    # Tracking
    is_read = models.BooleanField(default=False, help_text="Has the user read this notification")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notifications',
        help_text="Admin who created this notification"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was read")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "All Users"
        return f"{self.get_type_display()} to {user_str}: {self.title}"
