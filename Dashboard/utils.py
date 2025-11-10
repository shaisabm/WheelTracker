from datetime import datetime, time
from decimal import Decimal
import pytz


def auto_close_expired_positions():
    """
    Automatically manage position expiration status:
    1. Close open positions that have expired (at 4:00 PM ET on expiration date)
    2. Reopen closed positions where expiration was extended to a future date

    For auto-closed positions:
    - Sets close_date to expiration date
    - Sets premium_paid_to_close to 0
    - Sets close_fees to 0

    For reopened positions (extended expiration):
    - Clears close_date, premium_paid_to_close, and close_fees
    """
    from Dashboard.models import Position

    # Get current time in ET timezone
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    today_et = now_et.date()

    # Define 4:00 PM ET as the closing time
    closing_time = time(16, 0)  # 4:00 PM

    closed_count = 0
    reopened_count = 0

    # PART 1: Close expired open positions
    open_positions = Position.objects.filter(close_date__isnull=True)

    for position in open_positions:
        # Check if position has expired
        if position.expiration < today_et:
            # Past expiration date - close immediately
            position.close_date = position.expiration
            position.premium_paid_to_close = Decimal('0.00')
            position.close_fees = Decimal('0.00')
            position.save()
            closed_count += 1
        elif position.expiration == today_et and now_et.time() >= closing_time:
            # Today is expiration date and it's past 4:00 PM ET - close now
            position.close_date = position.expiration
            position.premium_paid_to_close = Decimal('0.00')
            position.close_fees = Decimal('0.00')
            position.save()
            closed_count += 1

    # PART 2: Reopen closed positions where expiration was extended
    # Only reopen positions that were auto-closed (premium_paid_to_close = 0 and close_fees = 0)
    closed_positions = Position.objects.filter(
        close_date__isnull=False,
        premium_paid_to_close=Decimal('0.00'),
        close_fees=Decimal('0.00')
    )

    for position in closed_positions:
        # Check if expiration is in the future or today before 4:00 PM ET
        if position.expiration > today_et:
            # Expiration is in the future - reopen
            position.close_date = None
            position.premium_paid_to_close = None
            position.close_fees = None
            position.save()
            reopened_count += 1
        elif position.expiration == today_et and now_et.time() < closing_time:
            # Expiration is today but before 4:00 PM ET - reopen
            position.close_date = None
            position.premium_paid_to_close = None
            position.close_fees = None
            position.save()
            reopened_count += 1

    return {'closed': closed_count, 'reopened': reopened_count}