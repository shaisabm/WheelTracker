#!/usr/bin/env python
"""
Script to create sample positions for testing the Wheel Strategy Tracker
Run with: python create_sample_data.py
"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WheelTracker.settings')
django.setup()

from Dashboard.models import Position

def create_sample_positions():
    """Create sample positions for testing"""

    print("Creating sample positions...")

    # Clear existing positions
    Position.objects.all().delete()

    # Sample position 1: Open Put
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=15),
        stock='AAPL',
        set_number=1,
        expiration=datetime.now().date() + timedelta(days=30),
        type='P',
        num_contracts=2,
        strike=Decimal('170.00'),
        premium=Decimal('3.50'),
        open_fees=Decimal('1.30'),
        assigned='No',
        notes='First wheel attempt with AAPL'
    )

    # Sample position 2: Closed Put (profitable)
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=45),
        stock='TSLA',
        set_number=1,
        expiration=datetime.now().date() - timedelta(days=1),
        type='P',
        num_contracts=1,
        strike=Decimal('220.00'),
        premium=Decimal('5.00'),
        open_fees=Decimal('0.65'),
        close_date=datetime.now().date() - timedelta(days=10),
        assigned='No',
        premium_paid_to_close=Decimal('2.00'),
        close_fees=Decimal('0.65'),
        notes='Closed early for profit'
    )

    # Sample position 3: Open Call
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=5),
        stock='MSFT',
        set_number=1,
        expiration=datetime.now().date() + timedelta(days=20),
        type='C',
        num_contracts=3,
        strike=Decimal('380.00'),
        premium=Decimal('4.20'),
        open_fees=Decimal('1.95'),
        assigned='No',
        notes='Covered calls on assigned shares'
    )

    # Sample position 4: Closed Call (assigned)
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=60),
        stock='NVDA',
        set_number=1,
        expiration=datetime.now().date() - timedelta(days=5),
        type='C',
        num_contracts=1,
        strike=Decimal('850.00'),
        premium=Decimal('12.00'),
        open_fees=Decimal('0.65'),
        close_date=datetime.now().date() - timedelta(days=5),
        assigned='Yes',
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00'),
        notes='Shares called away - completed wheel'
    )

    # Sample position 5: Open Put (second set)
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=7),
        stock='AAPL',
        set_number=2,
        expiration=datetime.now().date() + timedelta(days=25),
        type='P',
        num_contracts=1,
        strike=Decimal('165.00'),
        premium=Decimal('2.80'),
        open_fees=Decimal('0.65'),
        assigned='No',
        notes='Second wheel cycle with AAPL'
    )

    # Sample position 6: Closed Put (loss - rolled)
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=40),
        stock='META',
        set_number=1,
        expiration=datetime.now().date() - timedelta(days=15),
        type='P',
        num_contracts=2,
        strike=Decimal('480.00'),
        premium=Decimal('6.00'),
        open_fees=Decimal('1.30'),
        close_date=datetime.now().date() - timedelta(days=16),
        assigned='No',
        premium_paid_to_close=Decimal('8.50'),
        close_fees=Decimal('1.30'),
        notes='Rolled to avoid assignment'
    )

    # Sample position 7: Open Put (after roll)
    Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=16),
        stock='META',
        set_number=1,
        expiration=datetime.now().date() + timedelta(days=15),
        type='P',
        num_contracts=2,
        strike=Decimal('475.00'),
        premium=Decimal('7.00'),
        open_fees=Decimal('1.30'),
        assigned='No',
        notes='Rolled position from previous put'
    )

    print(f"Created {Position.objects.count()} sample positions!")
    print("\nPositions by stock:")
    for stock in Position.objects.values_list('stock', flat=True).distinct().order_by('stock'):
        count = Position.objects.filter(stock=stock).count()
        open_count = Position.objects.filter(stock=stock, close_date__isnull=True).count()
        print(f"  {stock}: {count} total ({open_count} open)")

if __name__ == '__main__':
    create_sample_positions()
