import json
import os

class AppManager:
    """The main controller for all business logic and data handling."""
    data_file = ""
    save_path = ""

    def __init__(self, save_path):
        self.save_path = save_path
        self._load_data()

    @classmethod
    def init_file_path(cls,data_file="\\data.json"):
        absolute_path = os.path.dirname(__file__)
        relative_path = r"..\data"
        cls.data_path = os.path.normpath(os.path.join(absolute_path, relative_path))
        cls.save_file = cls.data_path + data_path
    
    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                # populate object lists here
        
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Data file not found. Starting with a clean state.")
