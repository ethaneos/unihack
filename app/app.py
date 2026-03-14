import json
import os
from app.bank_cleaner import CSVCleaner
from app.model import RecurringPaymentAnalyzer

class AppManager:
    """The main controller for all business logic and data handling."""

    def __init__(self, data_file="\\data.json"):
        self.save_path = AppManager.init_file_path(data_file)
        self._load_data()

    @staticmethod
    def init_file_path(data_file):
        absolute_path = os.path.dirname(__file__)
        relative_path = r"..\data"
        data_path = os.path.normpath(os.path.join(absolute_path, relative_path))
        save_path = data_path + data_file

        return save_path
    
    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                # populate object lists here
        
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Data file not found. Starting with a clean state.")

    def analyse_bank_csv(self, bank_name, csv_path):
        cleaner = CSVCleaner()
        cleaned_df = cleaner.clean_bank_csv(csv_path, bank_name)
        
        # Initialize analyzer with cleaned data
        analyzer = RecurringPaymentAnalyzer(cleaned_df)
        
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
        results.to_csv('data/recurring_payment_analysis.csv', index=False)
