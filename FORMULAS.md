# Wheel Strategy Tracker - Formula Reference

This document details all the calculated fields and their formulas.

## Basic Calculations

### Days In Trade
```
If position is closed:
    days_in_trade = close_date - open_date
If position is open:
    days_in_trade = today - open_date
```

### Days To Expiration (DTE)
```
If position is closed:
    days_to_expiration = 0
If position is open:
    days_to_expiration = max(0, expiration_date - today)
```

### Days Open to Expiration
```
days_open_to_expiration = expiration_date - open_date
```

### Collateral Requirement
```
collateral_requirement = strike * 100 * num_contracts
```

For cash-secured puts, this represents the amount of capital you need to secure the position.
For covered calls, this would typically be based on your cost basis, but we use strike as an approximation.

### Risk Less Premium
```
premium_collected = (premium * num_contracts * 100) - open_fees
risk_less_premium = collateral_requirement - premium_collected
```

This is the actual capital at risk after accounting for the premium you collected.

## Profit/Loss Calculation

### Profit/Loss (Closed Positions Only)
```
premium_paid = premium_paid_to_close OR 0
close_fees_val = close_fees OR 0

gross_profit = (premium - premium_paid) * num_contracts * 100
total_fees = open_fees + close_fees_val

profit_loss = gross_profit - total_fees
```

**Example:**
- Sell put for $3.50 premium, 2 contracts, $1.30 open fees
- Buy to close for $1.50, $1.30 close fees
- Gross profit: ($3.50 - $1.50) × 2 × 100 = $400
- Total fees: $1.30 + $1.30 = $2.60
- Net P/L: $400 - $2.60 = $397.40

## Annualized Return Calculations

### AR% if Held to Expiration
```
premium_less_fees = (premium * num_contracts * 100) - open_fees
risk = risk_less_premium

ar_if_held_to_expiration = (365 × premium_less_fees / risk / days_open_to_expiration) × 100
```

This shows the annualized return if you hold the position through expiration and it expires worthless.

**Example:**
- Premium: $3.50 per contract
- 2 contracts, $1.30 fees
- Strike: $170
- 45 days from open to expiration
- Premium less fees: ($3.50 × 2 × 100) - $1.30 = $698.70
- Collateral: $170 × 100 × 2 = $34,000
- Risk less premium: $34,000 - $698.70 = $33,301.30
- AR%: (365 × $698.70 / $33,301.30 / 45) × 100 = 17.03%

### AR% of Closed Trade
```
profit_loss = calculated P/L from above
risk = risk_less_premium
days = days_in_trade

ar_of_closed_trade = (365 × profit_loss / risk / days) × 100
```

This is your actual annualized return for a closed position.

**Example:**
- Net P/L: $397.40
- Risk less premium: $33,301.30
- Days held: 35
- AR%: (365 × $397.40 / $33,301.30 / 35) × 100 = 12.46%

### AR% on Realized Premium (Open Positions)
```
premium_paid = current_option_price
close_fees_estimated = open_fees  # Estimate close fees same as open

gross_profit = (premium - premium_paid) * num_contracts * 100
realized_pl = gross_profit - open_fees - close_fees_estimated

risk = risk_less_premium
days = days_in_trade

ar_on_realized_premium = (365 × realized_pl / risk / days) × 100
```

This shows what your annualized return would be if you closed the position at the current market price.

**Example:**
- Premium received: $3.50
- Current price: $2.00
- 2 contracts, $1.30 open fees
- Days held: 15
- Estimated realized P/L: ($3.50 - $2.00) × 2 × 100 - $1.30 - $1.30 = $297.40
- Risk: $33,301.30
- AR%: (365 × $297.40 / $33,301.30 / 15) × 100 = 21.70%

### AR% on Remaining Premium (Open Positions)
```
cost_to_close = current_option_price * num_contracts * 100
risk = risk_less_premium
days = days_to_expiration

ar_on_remaining_premium = (365 × cost_to_close / risk / days) × 100
```

This shows the annualized return on the remaining value in the position through expiration.

**Example:**
- Current option price: $2.00
- 2 contracts
- 30 days to expiration
- Cost to close: $2.00 × 2 × 100 = $400
- Risk: $33,301.30
- AR%: (365 × $400 / $33,301.30 / 30) × 100 = 14.63%

## Other Metrics

### Percent Premium Earned
```
premium_earned = premium - current_option_price
percent_premium_earned = (premium_earned / premium) × 100
```

This shows what percentage of the original premium you've captured so far.

**Example:**
- Premium received: $3.50
- Current price: $2.00
- Premium earned: $3.50 - $2.00 = $1.50
- Percent earned: ($1.50 / $3.50) × 100 = 42.86%

### Set Break Even Price (Puts Only)
```
For puts only:
    total_premium_loss = max(0, premium_paid_to_close - premium)
    set_break_even_price = strike - total_premium_loss
```

This is a simplified calculation showing your break-even price if you get assigned on a put.

**Example:**
- Strike: $170
- Premium received: $3.50
- Closed for $5.00 (loss of $1.50)
- Break even: $170 - $1.50 = $168.50

**Note:** This is a basic calculation. For complex scenarios with multiple rolls at different strikes, the actual calculation would need to aggregate all positions in the set.

## Important Notes

1. **Premium Values:** All premium values in the database are per contract. The formulas multiply by 100 to get actual dollar values (since 1 contract = 100 shares).

2. **Fees:** Open fees and close fees should be entered as total amounts (not per contract), as different brokers charge in different ways.

3. **Collateral:** The collateral calculation assumes cash-secured puts. For covered calls, you might want to use your actual cost basis instead of the strike price for more accurate returns.

4. **Annualized Returns:** AR% calculations assume you can replicate the trade throughout the year. Actual returns may vary based on market conditions and available opportunities.

5. **Risk:** "Risk less premium" represents your actual capital at risk, which is the collateral minus the premium you collected upfront.

6. **Current Prices:** Yahoo Finance provides delayed data. For real-time calculations, consider integrating with a real-time data provider.

## Use Cases

### When to Use Each AR% Metric

- **AR% if Held to Expiration:** Use when opening a position to evaluate if the potential return meets your criteria.

- **AR% of Closed Trade:** Use to evaluate the actual performance of completed trades and compare against your targets.

- **AR% on Realized Premium:** Use to decide if you should take profits early. If this number is high, it might be worth closing the position.

- **AR% on Remaining Premium:** Use to decide if you should hold the position or roll it. If this number is low compared to other opportunities, consider rolling.

### Decision Making Example

You have an open put:
- AR% if Held to Expiration: 18%
- AR% on Realized Premium (current): 25%
- AR% on Remaining Premium: 8%
- Days to expiration: 20
- Days held: 15

**Analysis:**
- You've captured most of the value (25% annualized on 15 days is great)
- The remaining 20 days only offer 8% annualized
- You could close this position and potentially open a new one with better AR%
- Closing might free up capital for better opportunities
