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
    """Create sample positions demonstrating the wheel cycle tracking"""

    print("Creating sample positions with wheel cycle tracking...")

    # Clear existing positions
    Position.objects.all().delete()

    # AAPL Wheel Cycle #1 - Complete wheel
    print("\n=== AAPL Wheel Cycle #1 (Complete) ===")

    # Step 1: Sell put, get assigned
    aapl_put_1 = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=90),
        stock='AAPL',
        wheel_cycle_name='AAPL Wheel #1',
        expiration=datetime.now().date() - timedelta(days=45),
        type='P',
        num_contracts=1,
        strike=Decimal('165.00'),
        premium=Decimal('4.50'),
        open_fees=Decimal('0.65'),
        close_date=datetime.now().date() - timedelta(days=45),
        assigned='Yes',
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00'),
        notes='Got assigned - now own 100 shares at $165'
    )
    print(f"  1. Sold put at $165, got assigned")

    # Step 2: Sell covered call, get called away
    aapl_call_1 = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=40),
        stock='AAPL',
        wheel_cycle_name='AAPL Wheel #1',
        related_to=aapl_put_1,  # Link to previous position
        expiration=datetime.now().date() - timedelta(days=5),
        type='C',
        num_contracts=1,
        strike=Decimal('175.00'),
        premium=Decimal('3.20'),
        open_fees=Decimal('0.65'),
        close_date=datetime.now().date() - timedelta(days=5),
        assigned='Yes',
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00'),
        notes='Shares called away - completed wheel!'
    )
    print(f"  2. Sold covered call at $175, called away - WHEEL COMPLETE")

    # AAPL Wheel Cycle #2 - In progress
    print("\n=== AAPL Wheel Cycle #2 (In Progress) ===")

    # Step 1: Sell put (still open)
    aapl_put_2 = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=15),
        stock='AAPL',
        wheel_cycle_name='AAPL Wheel #2',
        expiration=datetime.now().date() + timedelta(days=30),
        type='P',
        num_contracts=2,
        strike=Decimal('170.00'),
        premium=Decimal('3.50'),
        open_fees=Decimal('1.30'),
        assigned='No',
        notes='Second wheel attempt with AAPL'
    )
    print(f"  1. Sold put at $170 - currently open")

    # TSLA - Single position (not part of wheel yet)
    print("\n=== TSLA - Standalone Position ===")
    tsla_put = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=45),
        stock='TSLA',
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
        notes='Closed early for profit - not part of wheel'
    )
    print(f"  Sold put at $220, closed for profit")

    # MSFT - In progress wheel
    print("\n=== MSFT Wheel (In Progress) ===")

    # Step 1: Sold put, got assigned
    msft_put = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=60),
        stock='MSFT',
        wheel_cycle_name='MSFT Jan Wheel',
        expiration=datetime.now().date() - timedelta(days=30),
        type='P',
        num_contracts=3,
        strike=Decimal('370.00'),
        premium=Decimal('5.80'),
        open_fees=Decimal('1.95'),
        close_date=datetime.now().date() - timedelta(days=30),
        assigned='Yes',
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00'),
        notes='Got assigned - now holding 300 shares'
    )
    print(f"  1. Sold put at $370, got assigned")

    # Step 2: Sell covered call (still open)
    msft_call = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=5),
        stock='MSFT',
        wheel_cycle_name='MSFT Jan Wheel',
        related_to=msft_put,
        expiration=datetime.now().date() + timedelta(days=20),
        type='C',
        num_contracts=3,
        strike=Decimal('380.00'),
        premium=Decimal('4.20'),
        open_fees=Decimal('1.95'),
        assigned='No',
        notes='Covered calls on assigned shares'
    )
    print(f"  2. Sold covered call at $380 - currently open")

    # META - Rolling scenario
    print("\n=== META - Rolling Scenario ===")

    # Step 1: First put (rolled)
    meta_put_1 = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=40),
        stock='META',
        wheel_cycle_name='META Roll',
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
    print(f"  1. Sold put at $480, closed at loss to roll")

    # Step 2: Rolled put (still open)
    meta_put_2 = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=16),
        stock='META',
        wheel_cycle_name='META Roll',
        related_to=meta_put_1,
        expiration=datetime.now().date() + timedelta(days=15),
        type='P',
        num_contracts=2,
        strike=Decimal('475.00'),
        premium=Decimal('7.00'),
        open_fees=Decimal('1.30'),
        assigned='No',
        notes='Rolled position from previous put'
    )
    print(f"  2. Rolled to put at $475 - currently open")

    # NVDA - Completed wheel
    print("\n=== NVDA - Completed Wheel ===")

    # Step 1: Put assigned
    nvda_put = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=120),
        stock='NVDA',
        wheel_cycle_name='NVDA Summer Wheel',
        expiration=datetime.now().date() - timedelta(days=65),
        type='P',
        num_contracts=1,
        strike=Decimal('820.00'),
        premium=Decimal('15.00'),
        open_fees=Decimal('0.65'),
        close_date=datetime.now().date() - timedelta(days=65),
        assigned='Yes',
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00'),
        notes='Assigned - bought shares at $820'
    )
    print(f"  1. Sold put at $820, got assigned")

    # Step 2: Call assigned
    nvda_call = Position.objects.create(
        open_date=datetime.now().date() - timedelta(days=60),
        stock='NVDA',
        wheel_cycle_name='NVDA Summer Wheel',
        related_to=nvda_put,
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
        notes='Shares called away - completed wheel!'
    )
    print(f"  2. Sold call at $850, called away - WHEEL COMPLETE")

    print(f"\n✓ Created {Position.objects.count()} sample positions!")

    # Show summary
    print("\n=== Summary ===")
    for cycle_name in Position.objects.filter(wheel_cycle_name__isnull=False).values_list('wheel_cycle_name', flat=True).distinct():
        positions = Position.objects.filter(wheel_cycle_name=cycle_name).order_by('open_date')
        print(f"\n{cycle_name}:")
        for pos in positions:
            status = "✓ Complete" if pos.assigned == 'Yes' else ("Open" if pos.is_open else "Closed")
            print(f"  - Step {pos.wheel_cycle_number}: {pos.get_type_display()} ${pos.strike} ({status})")

if __name__ == '__main__':
    create_sample_positions()
