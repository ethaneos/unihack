import json
import os
import pandas as pd
from io import StringIO
from datetime import datetime as dtdt
from app.bank_cleaner import CSVCleaner
from app.xgb_model import SubscriptionDetector

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

    def analyse_bank_csv(self, bank_name, csv):

        stringio = StringIO(csv.getvalue().decode("utf-8"), newline=None)
        csv_data = stringio.read()

        temp_file_name = dtdt.strftime(dtdt.now(), '%y-%m-%d-%H-%M-%S-%f') + ".csv"
        temp_file_path = os.path.join("data/temps/", temp_file_name)
        with open(f"{temp_file_path}", "w+") as f:
            f.write(csv_data)

        cleaner = CSVCleaner()
        cleaned_df = cleaner.clean_bank_csv(temp_file_path, bank_name)
        
        os.remove(temp_file_path)

        # Initialize analyzer with cleaned data
        detector = SubscriptionDetector()
        
        # Load and train
        training_set = detector.load_data("data/main_training_data.csv")
        detector.train(training_set)

        # Analyze and retrieve results
        results_df = detector.analyze(cleaned_df)
        return results_df
