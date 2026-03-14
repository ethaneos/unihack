import duckdb
import pandas as pd
import os

class CSVCleaner:
    """Cleans a csv for use in modelling
    For usage:
    e.g
    clean_bank_csv("Rabo.csv", "rabo", output_path="cleaned_rabo_data.csv")
    """
    # Define rules for CSV formats
    csv_configs = {
        "ubank": {
            "date_col": "Date and time",
            "date_format": "%H:%M %d-%m-%y",
            "desc_col": "Description",
            "debit_col": "Debit",
            # strip '$' and ',' then convert to float
            "debit_cleaning": "CAST(REPLACE(REPLACE(\"{debit_col}\", '$', ''), ',', '') AS FLOAT)"
        },
        "bank of melbourne": {
            "date_col": "Date",
            "date_format": "%d/%m/%Y",
            "desc_col": "Description",
            "debit_col": "Debit",
            # already numbers, just cast
            "debit_cleaning": "CAST(\"{debit_col}\" AS FLOAT)"
        },
        "westpac": {
            "date_col": "Date",
            "date_format": "%d/%m/%Y",
            "desc_col": "Narrative",
            "debit_col": "Debit Amount",
            # already numbers, just cast
            "debit_cleaning": "CAST(\"{debit_col}\" AS FLOAT)"
        },
        "macquarie": {
            "date_col": "Transaction Date",
            "date_format": "%d %b %Y",
            "desc_col": "Details",
            "debit_col": "Debit",
            # already numbers, just cast
            "debit_cleaning": "CAST(\"{debit_col}\" AS FLOAT)"       
        },
        "rabo": {
            "date_col": "Date",
            "date_format": "%d/%m/%Y",
            "desc_col": "Description",
            "debit_col": "Debit",
            # strip '$' and ',' then convert to float
            "debit_cleaning": "CAST(REPLACE(REPLACE(\"{debit_col}\", '$', ''), ',', '') AS FLOAT)"
        }
    }

    def __init__(self):
        pd.options.display.float_format = '{:.2f}'.format

    def clean_bank_csv(self, file_path, config_name, output_path=None):
        """
        params:
            file_path (str): The path to the raw CSV file.
            config_name (str): The name of the bank format (e.g., 'ubank').
            output_path (str, optional): The path to save the cleaned CSV. Defaults to None.
        """
        # if config_name not in csv_configs:
        #     raise ValueError(f"Unknown format: '{config_name}'. Available formats: {list(csv_configs.keys())}")
            
        config = CSVCleaner.csv_configs[config_name]
        
        sql_query = f"""
        SELECT 
            CAST(strptime("{config['date_col']}", '{config['date_format']}') AS DATE) AS date,
            "{config['desc_col']}" AS description,
            {config['debit_cleaning'].format(debit_col=config['debit_col'])} AS debit
        FROM read_csv_auto('{file_path}', all_varchar=True)
        WHERE "{config['debit_col']}" IS NOT NULL 
        AND TRIM("{config['debit_col']}") != '';
        """
        

        df = duckdb.query(sql_query).df()
        

        if output_path:
            df.to_csv(output_path, index=False)
            
        return df


