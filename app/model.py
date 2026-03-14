import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# raw_training = pd.read_csv("training_set.csv", index_col=False)
# raw_training = raw_training.loc[:, ['Date', 'Description', 'Debit']]
# raw_training

# raw_training['Date'] = pd.to_datetime(raw_training['Date']).dt.normalize()
# # raw_training['Debit'] = raw_training['Debit'].str.replace(',', '')
# # raw_training['Debit'] = raw_training['Debit'].str.replace('$', '')

# raw_training

# raw_training = raw_training[raw_training['Debit'] > 0]
# # cleaned_training = raw_training.drop(columns = ["Credit", "Balance"])
# cleaned_training = raw_training.copy()
# cleaned_training['YearMonth'] = cleaned_training['Date'].dt.to_period('M')
# cleaned_training['YearWeek'] = cleaned_training['Date'].dt.to_period('W')

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from difflib import SequenceMatcher
import re

def extract_merchant_name(description):
    """
    Extract core merchant name by removing codes, platforms, and noise
    """
    # Convert to uppercase for consistency
    text = str(description).upper()

    # Common patterns to remove/extract
    patterns_to_remove = [
        r'\*?P[A-Z0-9]{7,}',  # Remove *P[codes]
        r'\*',                # Replace * with space
        r'#\d+',              # Remove #123
        r'SYDNEY|VICTORIA|VIC|AU|AUSTRALIA',  # Remove location
        r'00:00:00|[0-9]{2}:[0-9]{2}:[0-9]{2}',  # Remove timestamps
        r'\d{1,2}[A-Z]{3}\d{1,2}:\d{2}',  # NEW: 22Jul12:14 format
        r'\d{1,2}[A-Z]{3}',   # Remove dates like 22Jul

    ]

    cleaned = text
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned)

    # Extract key words (usually first meaningful words)
    # Remove common prefixes
    prefixes = ['VISA', 'PURCHASE', 'EFTPOS', 'DEBIT', 'INTERNET', 'DEPOSIT',
                'WITHDRAWAL', 'OSKO', 'FROM', 'TO', 'PAYPAL', '*']

    words = cleaned.split()
    core_words = [w for w in words if w and w not in prefixes and len(w) > 2]

    # Return first 2-3 meaningful words
    merchant = ' '.join(core_words[:2]).strip()

    return merchant if merchant else description[:20]

cleaned_training['Merchant'] = cleaned_training['Description'].apply(extract_merchant_name)

# Group by Merchant + Debit amount to find patterns
merchant_debit_groups = cleaned_training.groupby(['Merchant', 'Debit']).agg({
    'Date': ['count', 'min', 'max', lambda x: list(x)],  # count, first date, last date, all dates
}).reset_index()

merchant_debit_groups.columns = ['Merchant', 'Debit', 'Count', 'First_Date', 'Last_Date', 'All_Dates']

# Filter: Only consider as potentially recurring if appears 2+ times
potential_recurring = merchant_debit_groups[merchant_debit_groups['Count'] >= 3].copy()
date_filtered = potential_recurring[potential_recurring["Last_Date"] >= pd.Timestamp('2026-01-01')].copy()
date_filtered

print(f"\nPotentially recurring combinations (Merchant + Amount): {len(date_filtered)}")
print(date_filtered.head(100))

import datetime
from collections import Counter

def categorize_interval(date_diff):
    if date_diff <= datetime.timedelta(days=8): # 7 days + 1 day buffer
        return 'Weekly'
    elif date_diff <= datetime.timedelta(days=15): # 14 days + 1 day buffer
        return 'Fortnightly'
    elif date_diff <= datetime.timedelta(days=32): # ~30 days + 2 day buffer
        return 'Monthly'
    elif date_diff <= datetime.timedelta(days=93): # ~90 days (3 months) + 3 day buffer
        return 'Quarterly'
    elif date_diff <= datetime.timedelta(days=185): # ~180 days (6 months) + 5 day buffer
        return 'Semi-Annually'
    elif date_diff <= datetime.timedelta(days=370): # ~365 days (1 year) + 5 day buffer
        return 'Annually'
    else:
        return 'Irregular'

# Function to analyze intervals for each group
def analyze_recurring_intervals(all_dates):
    """
    Analyze intervals and only mark as 'Mixed' if no pattern repeats 3+ times
    Otherwise return the dominant pattern

    Additional check: If payment reoccurs more than once within 1 week, it's not recurring
    """
    if len(all_dates) < 2:
        return 'Not enough data', 0.0, [], 'Insufficient data'

    sorted_dates = sorted(all_dates)
    intervals = []

    # ============================================
    # CHECK 1: Multiple payments within 1 week (likely errors/refunds)
    # ============================================


    consecutive_quick_payments = 0
    max_consecutive_quick = 0

    for i in range(1, len(sorted_dates)):
        diff = sorted_dates[i] - sorted_dates[i-1]

        # Check if this interval is suspiciously short (< 3 days = likely error/refund)
        if diff < datetime.timedelta(days=3):
            consecutive_quick_payments += 1
            max_consecutive_quick = max(max_consecutive_quick, consecutive_quick_payments)
        else:
            consecutive_quick_payments = 0

    # If there are 2+ consecutive quick payments, it's suspicious
    if max_consecutive_quick >= 2:
        return 'Not Recurring', 0.0, intervals, 'Multiple consecutive payments within 3 days (likely error/refund)'

    # ============================================
    # CHECK 2: Calculate intervals between consecutive dates
    # ============================================

    for i in range(1, len(sorted_dates)):
        diff = sorted_dates[i] - sorted_dates[i-1]
        interval_type = categorize_interval(diff)
        intervals.append(interval_type)

    # ============================================
    # CHECK 3: Count occurrences of each interval type
    # ============================================

    interval_counts = Counter(intervals)

    # Find the most common interval
    most_common_interval, most_common_count = interval_counts.most_common(1)[0]

    # ============================================
    # CHECK 4: If the most common interval appears 3+ times, it's the pattern
    # ============================================

    if most_common_count >= 3:
        confidence = most_common_count / len(intervals)
        return most_common_interval, confidence, intervals, 'Valid pattern'

    # ============================================
    # CHECK 5: If no pattern repeats 3+ times, it's mixed
    # ============================================

    else:
        return 'Mixed', 0.0, intervals, 'No pattern repeats 3+ times'

# Apply the function to the date_filtered DataFrame
date_filtered['Interval_Type'] = date_filtered['All_Dates'].apply(analyze_recurring_intervals)
print("Recurring payments with their identified intervals:")
print(date_filtered[['Merchant', 'Debit', 'Count', 'Interval_Type']])