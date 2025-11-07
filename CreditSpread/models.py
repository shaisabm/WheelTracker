from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime


class CreditSpread(models.Model):
    """Model for tracking credit spread option positions (Bull Put and Bear Call spreads)"""

    TYPE_CHOICES = [
        ('BPS', 'Bull Put Spread'),
        ('BCS', 'Bear Call Spread'),
    ]

    # User association
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_spreads', null=True)

    # User input fields
    open_date = models.DateField(help_text="The date that you open the spread")
    stock = models.CharField(max_length=10, help_text="The ticker of the underlying stock")
    expiration = models.DateField(help_text="The expiration date of the contracts")
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, help_text="BPS for Bull Put Spread or BCS for Bear Call Spread")

    # Long leg (bought option)
    long_strike = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="The strike price of the long leg (bought option)"
    )
    long_premium = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The premium paid for the long leg"
    )

    # Short leg (sold option)
    short_strike = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="The strike price of the short leg (sold option)"
    )
    short_premium = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The premium received for the short leg"
    )

    # Position details
    num_contracts = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="The number of spreads"
    )
    open_fees = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total commissions and fees paid to open the spread"
    )

    # Closing details
    close_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date you close the position"
    )
    long_close_premium = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The premium received for closing the long leg"
    )
    short_close_premium = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="The premium paid to close the short leg"
    )
    close_fees = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Commissions and fees paid to close the spread"
    )

    notes = models.TextField(
        blank=True,
        help_text="Any notes or comments about the spread"
    )

    # Current pricing (for open positions)
    current_long_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current price of the long leg"
    )
    current_short_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current price of the short leg"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-open_date', 'stock']
        indexes = [
            models.Index(fields=['stock']),
            models.Index(fields=['open_date']),
            models.Index(fields=['expiration']),
        ]

    def __str__(self):
        return f"{self.stock} - {self.get_type_display()} ${self.short_strike}/${self.long_strike} exp {self.expiration}"

    @property
    def is_open(self):
        """Check if the spread is still open"""
        return self.close_date is None

    @property
    def days_in_trade(self):
        """Calculate the number of days the trade was held"""
        if self.close_date:
            return (self.close_date - self.open_date).days
        return (datetime.now().date() - self.open_date).days

    @property
    def days_to_expiration(self):
        """Calculate the number of days remaining until expiration"""
        if self.close_date:
            return 0
        days = (self.expiration - datetime.now().date()).days
        return max(0, days)

    @property
    def net_credit(self):
        """
        Calculate the net credit received when opening the spread.

        Formula:
            gross_credit = (short_premium - long_premium) * num_contracts * 100
            net_credit = gross_credit - open_fees
        """
        # Calculate the gross credit received before fees
        gross_credit = (self.short_premium - self.long_premium) * self.num_contracts * 100
        # Subtract open fees to get the net credit
        return gross_credit - self.open_fees

    @property
    def max_risk(self):
        """Calculate maximum risk: (width of strikes * 100 * num_contracts) - net_credit"""
        width = abs(self.short_strike - self.long_strike)
        max_loss = width * 100 * self.num_contracts
        return max_loss - self.net_credit

    @property
    def max_profit(self):
        """Maximum profit is the net credit received"""
        return self.net_credit

    @property
    def profit_loss(self):
        """Calculate actual P/L for closed positions"""
        if self.close_date is None:
            return None

        long_close = self.long_close_premium or Decimal('0.00')
        short_close = self.short_close_premium or Decimal('0.00')
        close_fees_val = self.close_fees or Decimal('0.00')

        # Opening: We received short_premium and paid long_premium
        opening_credit = self.short_premium - self.long_premium

        # Closing: We receive long_close and pay short_close
        closing_credit = long_close - short_close

        # Total P/L
        total_credit = (opening_credit + closing_credit) * self.num_contracts * 100
        total_fees = self.open_fees + close_fees_val

        return total_credit - total_fees

    @property
    def roi_percentage(self):
        """
        Calculate the maximum possible ROI: (net_credit / max_risk) * 100

        This represents the maximum theoretical ROI if the position is held to
        expiration and achieves full profit (credit spread expires worthless).
        For closed positions, use profit_loss to calculate actual realized ROI.

        Returns:
            Decimal or None: ROI percentage, or None if max_risk <= 0
        """
        if self.max_risk <= 0:
            return None
        return (self.net_credit / self.max_risk) * 100

    @property
    def ar_if_held_to_expiration(self):
        """Calculate Annualized Return if held to expiration"""
        days_open_to_exp = (self.expiration - self.open_date).days
        if days_open_to_exp == 0 or self.max_risk <= 0:
            return None
        return (Decimal('365') / days_open_to_exp) * (self.net_credit / self.max_risk) * 100

    @property
    def ar_of_closed_trade(self):
        """Calculate actual Annualized Return for closed trades"""
        if self.close_date is None or self.days_in_trade == 0 or self.max_risk <= 0:
            return None

        pl = self.profit_loss
        if pl is None:
            return None

        return (Decimal('365') / self.days_in_trade) * (pl / self.max_risk) * 100

    @property
    def current_profit_loss(self):
        """Calculate unrealized P/L for open positions"""
        if self.close_date is not None:
            return None

        if self.current_long_price is None or self.current_short_price is None:
            return None

        # Opening credit
        opening_credit = self.short_premium - self.long_premium

        # Current value if we closed now
        current_credit = self.current_long_price - self.current_short_price

        # Total unrealized P/L
        total_credit = (opening_credit + current_credit) * self.num_contracts * 100

        # Estimate close fees same as open fees
        estimated_close_fees = self.open_fees

        return total_credit - self.open_fees - estimated_close_fees

    @property
    def break_even_price(self):
        """Calculate break-even price"""
        net_credit_per_contract = self.net_credit / self.num_contracts / 100

        if self.type == 'BPS':
            # For Bull Put Spread: short_strike - net_credit
            return self.short_strike - net_credit_per_contract
        else:
            # For Bear Call Spread: short_strike + net_credit
            return self.short_strike + net_credit_per_contract
