"""
Recurring Payment Analyzer - Object Oriented Implementation
Analyzes financial transaction data to identify and classify recurring payments.
"""
import pandas as pd
import datetime
import re
from collections import Counter

class RecurringPaymentAnalyzer:
    """
    A class to analyze and identify recurring payments from transaction data.
    
    Attributes:
        df (pd.DataFrame): The input dataframe with columns: 'date', 'description', 'debit'
        merchant_column (str): Name of the merchant column after extraction
        results_df (pd.DataFrame): Results dataframe with recurring payment analysis
    """
    
    def __init__(self, df):
        """
        Initialize the RecurringPaymentAnalyzer with transaction data.
        
        Args:
            df (pd.DataFrame): Input dataframe with columns ['date', 'description', 'debit']
                              - date: datetime
                              - description: str
                              - debit: float
        
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        # Validate input dataframe
        required_columns = ['date', 'description', 'debit']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        # Create a copy to avoid modifying original data
        self.df = df.copy()
        self.results_df = None
        
        print("✓ RecurringPaymentAnalyzer initialized")
    
    # ============================================
    # MERCHANT EXTRACTION
    # ============================================
    
    def _extract_merchant_name(self, description):
        """
        Extract core merchant name by removing codes, platforms, and noise.
        
        This method cleans transaction descriptions to isolate the actual merchant name
        by removing transaction codes, timestamps, locations, and common prefixes.
        
        Args:
            description (str): The raw transaction description
            
        Returns:
            str: Cleaned merchant name or first 20 characters if extraction fails
            
        Example:
            >>> analyzer._extract_merchant_name("Eftpos Debit 22Jul12:14 Paypal *Spotify*P38Cd9648Sydney Au")
            'SPOTIFY'
        """
        # Convert to uppercase for consistent processing
        text = str(description).upper()
        
        # Define regex patterns to remove unwanted elements
        patterns_to_remove = [
            r'\*?P[A-Z0-9]{7,}',           # Remove P[codes] or *P[codes]
            r'\*',                          # Remove asterisks
            r'#\d+',                        # Remove #123 style codes
            r'SYDNEY|VICTORIA|VIC|AU|AUSTRALIA',  # Remove location names
            r'\d{1,2}[A-Z]{3}\d{1,2}:\d{2}',      # Remove 22Jul12:14 format
            r'\d{1,2}[A-Z]{3}',                   # Remove 22Jul format
            r'\d{2}:\d{2}:\d{2}',                 # Remove HH:MM:SS
            r'\d{2}:\d{2}',                       # Remove HH:MM
            r'\d{10,}',                           # Remove long numbers (account IDs)
        ]
        
        # Apply all regex patterns to clean the text
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, ' ', cleaned)
        
        # Define common transaction prefixes to exclude
        prefixes = [
            'VISA', 'PURCHASE', 'EFTPOS', 'DEBIT', 'INTERNET', 'DEPOSIT',
            'WITHDRAWAL', 'OSKO', 'FROM', 'TO', 'PAYPAL', 'SCT', 'CTRLINK',
            'ATM', 'CREDIT', 'EASYPARK', 'MYKI', 'FOR', 'MCARE', 'ATO'
        ]
        
        # Extract core words (words not in prefixes and with length > 2)
        words = cleaned.split()
        core_words = [w for w in words if w and w not in prefixes and len(w) > 2]
        
        # Return first 2 meaningful words as merchant name
        merchant = ' '.join(core_words[:2]).strip()
        
        return merchant if merchant else description[:20]
    
    def extract_merchants(self):
        """
        Extract merchant names for all transactions in the dataframe.
        
        Creates a new 'merchant' column by applying merchant extraction to all descriptions.
        
        Returns:
            pd.DataFrame: Modified dataframe with added 'merchant' column
        """
        self.df['merchant'] = self.df['description'].apply(self._extract_merchant_name)
        print(f"✓ Extracted merchants for {len(self.df)} transactions")
        return self.df
    
    # ============================================
    # MERCHANT GROUPING
    # ============================================
    
    def group_transactions(self, min_occurrences=3, min_date=None):
        """
        Group transactions by merchant and debit amount to identify potential recurring patterns.
        
        This method groups transactions with the same merchant name and debit amount,
        counting occurrences and collecting all transaction dates for each group.
        
        Args:
            min_occurrences (int): Minimum number of transactions to be considered recurring (default: 3)
            min_date (pd.Timestamp or str): Filter groups with last transaction on/after this date (default: None)
            
        Returns:
            pd.DataFrame: Grouped dataframe with columns:
                - merchant: Merchant name
                - debit: Transaction amount
                - count: Number of occurrences
                - first_date: Date of first transaction
                - last_date: Date of last transaction
                - all_dates: List of all transaction dates
                
        Example:
            >>> grouped = analyzer.group_transactions(min_occurrences=3, min_date='2026-01-01')
        """
        # Group by merchant and debit amount
        grouped = self.df.groupby(['merchant', 'debit']).agg({
            'date': [
                'count',                    # Number of occurrences
                'min',                      # First transaction date
                'max',                      # Last transaction date
                lambda x: list(x)          # All transaction dates
            ]
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['merchant', 'debit', 'count', 'first_date', 'last_date', 'all_dates']
        
        # Filter by minimum occurrences
        grouped = grouped[grouped['count'] >= min_occurrences]
        
        # Filter by minimum date if provided
        if min_date is not None:
            min_date = pd.Timestamp(min_date)
            grouped = grouped[grouped['last_date'] >= min_date]
        
        self.grouped_df = grouped.copy()
        print(f"✓ Found {len(grouped)} recurring transaction groups (>= {min_occurrences} occurrences)")
        
        return grouped
    
    # ============================================
    # INTERVAL ANALYSIS
    # ============================================
    
    @staticmethod
    def _categorize_interval(date_diff):
        """
        Categorize a time interval into a frequency type.
        
        Maps days between transactions into standard frequency categories
        with built-in buffers for slight variations.
        
        Args:
            date_diff (datetime.timedelta): Time difference between transactions
            
        Returns:
            str: Frequency category (Weekly, Monthly, Quarterly, etc.)
            
        Categories:
            - Weekly: <= 8 days (7 + 1 buffer)
            - Fortnightly: <= 15 days (14 + 1 buffer)
            - Monthly: <= 32 days (30 + 2 buffer)
            - Quarterly: <= 93 days (90 + 3 buffer)
            - Semi-Annually: <= 185 days (180 + 5 buffer)
            - Annually: <= 370 days (365 + 5 buffer)
            - Irregular: > 370 days
        """
        if date_diff <= datetime.timedelta(days=8):
            return 'Weekly'
        elif date_diff <= datetime.timedelta(days=15):
            return 'Fortnightly'
        elif date_diff <= datetime.timedelta(days=32):
            return 'Monthly'
        elif date_diff <= datetime.timedelta(days=93):
            return 'Quarterly'
        elif date_diff <= datetime.timedelta(days=185):
            return 'Semi-Annually'
        elif date_diff <= datetime.timedelta(days=370):
            return 'Annually'
        else:
            return 'Irregular'
    
    @staticmethod
    def _analyze_recurring_intervals(all_dates):
        """
        Analyze transaction dates to identify recurring payment patterns.
        
        Examines the intervals between consecutive transactions and identifies
        if they follow a consistent pattern. Requires at least 3 occurrences
        of the same interval type to be considered a valid pattern.
        
        Also checks for suspicious rapid transactions (likely errors/refunds):
        - Flags if 2+ consecutive transactions occur within 3 days
        
        Args:
            all_dates (list): List of transaction dates
            
        Returns:
            tuple: (interval_type, confidence, intervals, validation_reason)
                - interval_type (str): Most common interval or 'Mixed'/'Not Recurring'
                - confidence (float): 0-1 score of pattern consistency
                - intervals (list): List of all interval categories
                - validation_reason (str): Explanation of the result
        """
        # Check if sufficient data
        if len(all_dates) < 2:
            return 'Not enough data', 0.0, [], 'Insufficient data'
        
        # Sort dates chronologically
        sorted_dates = sorted(all_dates)
        intervals = []
        
        # ============================================
        # CHECK 1: Detect suspicious rapid transactions
        # ============================================
        
        consecutive_quick_payments = 0
        max_consecutive_quick = 0
        
        for i in range(1, len(sorted_dates)):
            diff = sorted_dates[i] - sorted_dates[i-1]
            
            # Flag transactions within 3 days as potentially erroneous
            if diff < datetime.timedelta(days=3):
                consecutive_quick_payments += 1
                max_consecutive_quick = max(max_consecutive_quick, consecutive_quick_payments)
            else:
                consecutive_quick_payments = 0
        
        # If 2+ consecutive quick payments detected, likely error/refund
        if max_consecutive_quick >= 2:
            return 'Not Recurring', 0.0, intervals, 'Multiple consecutive payments < 3 days (likely error/refund)'
        
        # ============================================
        # CHECK 2: Calculate intervals between transactions
        # ============================================
        
        for i in range(1, len(sorted_dates)):
            diff = sorted_dates[i] - sorted_dates[i-1]
            interval_type = RecurringPaymentAnalyzer._categorize_interval(diff)
            intervals.append(interval_type)
        
        # ============================================
        # CHECK 3: Count occurrences of each interval type
        # ============================================
        
        interval_counts = Counter(intervals)
        most_common_interval, most_common_count = interval_counts.most_common(1)[0]
        
        # ============================================
        # CHECK 4: Validate pattern consistency
        # ============================================
        
        # Pattern must repeat at least 3 times to be valid
        if most_common_count >= 3:
            confidence = most_common_count / len(intervals)
            return most_common_interval, confidence, intervals, 'Valid pattern'
        
        # Otherwise, pattern is inconsistent/mixed
        else:
            return 'Mixed', 0.0, intervals, 'No pattern repeats 3+ times'
    
    def analyze_intervals(self):
        """
        Analyze payment intervals for all grouped transactions.
        
        Applies interval analysis to each recurring transaction group
        to determine the frequency pattern and confidence score.
        
        Returns:
            pd.DataFrame: Updated grouped dataframe with interval analysis columns:
                - interval_type: Identified frequency pattern
                - pattern_confidence: 0-1 confidence score
                - all_intervals: List of calculated intervals
                - validation_reason: Explanation of the result
        """
        if self.grouped_df is None:
            raise ValueError("Run group_transactions() first")
        
        # Apply interval analysis to all groups
        result = self.grouped_df['all_dates'].apply(self._analyze_recurring_intervals)
        
        # Unpack results into separate columns
        self.grouped_df['interval_type'] = result.apply(lambda x: x[0])
        self.grouped_df['pattern_confidence'] = result.apply(lambda x: x[1])
        self.grouped_df['all_intervals'] = result.apply(lambda x: x[2])
        self.grouped_df['validation_reason'] = result.apply(lambda x: x[3])
        
        print(f"✓ Interval analysis completed")
        
        return self.grouped_df
    
    # ============================================
    # RESULTS AND REPORTING
    # ============================================
    
    def get_valid_recurring(self):
        """
        Get only the valid recurring payments (high confidence patterns).
        
        Returns:
            pd.DataFrame: Filtered dataframe containing only payments with
                         valid patterns (interval_type != 'Mixed' and != 'Not Recurring')
        """
        if self.grouped_df is None:
            raise ValueError("Run analyze_intervals() first")
        
        valid = self.grouped_df[
            (self.grouped_df['interval_type'] != 'Mixed') &
            (self.grouped_df['interval_type'] != 'Not Recurring')
        ]
        
        print(f"✓ Found {len(valid)} valid recurring payments")
        return valid
    
    def get_mixed_patterns(self):
        """
        Get transactions with mixed/inconsistent patterns.
        
        Returns:
            pd.DataFrame: Filtered dataframe containing only payments with
                         no consistent pattern (interval_type == 'Mixed')
        """
        if self.grouped_df is None:
            raise ValueError("Run analyze_intervals() first")
        
        mixed = self.grouped_df[self.grouped_df['interval_type'] == 'Mixed']
        return mixed
    
    def get_flagged_payments(self):
        """
        Get flagged payments (errors/refunds/suspicious).
        
        Returns:
            pd.DataFrame: Filtered dataframe containing only payments flagged
                         as potentially erroneous (interval_type == 'Not Recurring')
        """
        if self.grouped_df is None:
            raise ValueError("Run analyze_intervals() first")
        
        flagged = self.grouped_df[self.grouped_df['interval_type'] == 'Not Recurring']
        return flagged
    
    def print_summary(self):
        """
        Print a formatted summary of the recurring payment analysis results.
        
        Displays:
        - Valid recurring payments
        - Mixed/inconsistent patterns
        - Flagged suspicious payments
        - Summary statistics
        """
        if self.grouped_df is None:
            raise ValueError("Run analyze_intervals() first")
        
        print("\n" + "="*80)
        print("=== RECURRING PAYMENT ANALYSIS SUMMARY ===\n")
        
        # Valid patterns
        valid = self.get_valid_recurring()
        print(f"✓ VALID RECURRING PAYMENTS ({len(valid)}):")
        print(valid[['merchant', 'debit', 'count', 'interval_type', 'pattern_confidence']].to_string())
        
        # Mixed patterns
        mixed = self.get_mixed_patterns()
        if len(mixed) > 0:
            print(f"\n⚠ MIXED PATTERNS ({len(mixed)}):")
            print(mixed[['merchant', 'debit', 'count', 'validation_reason']].to_string())
        
        # Flagged payments
        flagged = self.get_flagged_payments()
        if len(flagged) > 0:
            print(f"\n✗ FLAGGED PAYMENTS ({len(flagged)}):")
            print(flagged[['merchant', 'debit', 'count', 'validation_reason']].to_string())
        
        print("\n" + "="*80)
    
    # ============================================
    # EXECUTION PIPELINE
    # ============================================
    
    def run_analysis(self, min_occurrences=3, min_date=None):
        """
        Execute the complete recurring payment analysis pipeline.
        
        Runs all analysis steps in sequence:
        1. Extract merchant names from descriptions
        2. Group transactions by merchant and amount
        3. Analyze payment intervals
        4. Print summary results
        
        Args:
            min_occurrences (int): Minimum transactions for recurring pattern (default: 3)
            min_date (str or pd.Timestamp): Filter for transactions after this date (default: None)
            
        Returns:
            pd.DataFrame: Grouped dataframe with complete analysis results
            
        Example:
            >>> analyzer = RecurringPaymentAnalyzer(df)
            >>> results = analyzer.run_analysis(min_occurrences=3, min_date='2026-01-01')
        """
        print("\n" + "="*80)
        print("=== STARTING RECURRING PAYMENT ANALYSIS ===\n")
        
        # Step 1: Extract merchants
        self.extract_merchants()
        
        # Step 2: Group transactions
        self.group_transactions(min_occurrences=min_occurrences, min_date=min_date)
        
        # Step 3: Analyze intervals
        self.analyze_intervals()
        
        # Step 4: Print summary
        self.print_summary()
        
        self.results_df = self.grouped_df.copy()
        
        print("\n✓ Analysis complete!")
        
        return self.results_df


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    """
    Example usage of the RecurringPaymentAnalyzer class.
    
    Assumes cleaned_training is already loaded with columns:
    - 'date' (datetime)
    - 'description' (str)
    - 'debit' (float)
    """
    import os
    cwd = os.getcwd()
    file_path = os.path.join(cwd, "data", "example_training_set.csv")
    
    raw_training = pd.read_csv(file_path, index_col=False)

    raw_training = raw_training.loc[:, ['Date', 'Description', 'Debit']]
    raw_training = raw_training.rename(columns={'Date': 'date', 'Description': 'description', 'Debit': 'debit'})

    raw_training['date'] = pd.to_datetime(raw_training['date']).dt.normalize()
    raw_training = raw_training[raw_training['debit'] > 0]
    cleaned_training = raw_training.copy()
    cleaned_training['YearMonth'] = cleaned_training['date'].dt.to_period('M')
    cleaned_training['YearWeek'] = cleaned_training['date'].dt.to_period('W')

    # Initialize analyzer with cleaned data
    analyzer = RecurringPaymentAnalyzer(cleaned_training)
    
    # Run complete analysis
    results = analyzer.run_analysis(
        min_occurrences=3,           # Minimum 3 occurrences
        min_date='2026-01-01'        # Only recent transactions
    )
    
    # Access specific results
    valid_recurring = analyzer.get_valid_recurring()
    mixed_patterns = analyzer.get_mixed_patterns()
    flagged_payments = analyzer.get_flagged_payments()
    
    # Save results
    results.to_csv('recurring_payment_analysis.csv', index=False)