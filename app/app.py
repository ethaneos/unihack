import json
import os

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
