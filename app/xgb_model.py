import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from xgboost import XGBClassifier


class SubscriptionDetector:
    """Detects and analyzes recurring subscription transactions from bank statements."""
    
    def __init__(self):
        """Initialize the detector with predefined patterns and model parameters."""
        self.model = XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8
        )
        self.tfidf = None
        self.subscriptions = [
            "GYM MEMBERSHIP", "ZOO MEMBERSHIP", "SPOTIFY", "NETFLIX",
            "YOUTUBE", "MORTGAGE", "NOTABILITY"
        ]
        self.cadence_days = {
            "WEEKLY": 7,
            "FORTNIGHTLY": 14,
            "MONTHLY": 30,
            "QUARTERLY": 90,
            "SEMI_ANNUAL": 182,
            "ANNUAL": 365
        }
    
    def load_data(self, filepath):
        """Load and normalize transaction data from CSV."""
        df = pd.read_csv(filepath, index_col=False)
        df['date'] = pd.to_datetime(df['date'], dayfirst=True).dt.normalize()
        df = df[df['debit'] > 0]
        return df
    
    def extract_merchant_name(self, description):
        """Extract clean merchant name from transaction description."""
        text = str(description).upper()
        
        patterns_to_remove = [
            r'\*?P[A-Z0-9]{7,}',
            r'\*',
            r'#\d+',
            r'SYDNEY|VICTORIA|VIC|AU|AUSTRALIA',
            r'\d{1,2}[A-Z]{3}\d{1,2}:\d{2}',
            r'\d{1,2}[A-Z]{3}',
            r'\d{2}:\d{2}:\d{2}',
            r'\d{2}:\d{2}',
            r'\d{10,}',
        ]
        
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, ' ', cleaned)
        
        prefixes = [
            'VISA', 'PURCHASE', 'EFTPOS', 'DEBIT', 'INTERNET', 'DEPOSIT',
            'WITHDRAWAL', 'OSKO', 'FROM', 'TO', 'PAYPAL', 'SCT', 'CTRLINK',
            'ATM', 'CREDIT', 'EASYPARK', 'MYKI', 'FOR', 'MCARE', 'ATO'
        ]
        
        words = cleaned.split()
        core_words = [w for w in words if w not in prefixes and len(w) > 2]
        merchant = " ".join(core_words[:2]).strip()
        
        return merchant if merchant else text[:20]
    
    def feature_engineering(self, df, fit=False):
        """Extract and engineer features from transaction data."""
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        
        # Time features
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["month"] = df["date"].dt.month
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
        
        # Amount features
        df["amount_abs"] = df["debit"].abs()
        df["amount_round"] = df["amount_abs"].round(1)
        
        # Merchant extraction
        df["merchant"] = df["description"].apply(self.extract_merchant_name)
        
        # Merchant frequency
        merchant_counts = df["merchant"].value_counts()
        df["merchant_freq"] = df["merchant"].map(merchant_counts)
        
        # Time interval features
        df = df.sort_values("date")
        df["days_since_last"] = df.groupby("merchant")["date"].diff().dt.days.fillna(0)
        df["interval_std"] = df.groupby("merchant")["days_since_last"].transform("std").fillna(0)
        df["amount_std"] = df.groupby("merchant")["amount_abs"].transform("std").fillna(0)
        
        # TFIDF vectorization
        if fit:
            self.tfidf = TfidfVectorizer(max_features=200)
            tfidf_matrix = self.tfidf.fit_transform(df["merchant"])
        else:
            tfidf_matrix = self.tfidf.transform(df["merchant"])
        
        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=self.tfidf.get_feature_names_out(),
            index=df.index
        )
        
        numeric_features = df[[
            "amount_abs", "amount_round", "day_of_week", "day_of_month",
            "month", "merchant_freq", "days_since_last", "interval_std", "amount_std"
        ]]
        
        X = pd.concat([numeric_features, tfidf_df], axis=1)
        return X, df
    
    def train(self, training_data):
        """Train model on labeled training data."""
        X_train, df_train = self.feature_engineering(training_data, fit=True)
        df_train["is_recurring"] = 0
        df_train.loc[df_train["merchant"].isin(self.subscriptions), "is_recurring"] = 1
        y_train = df_train["is_recurring"]
        self.model.fit(X_train, y_train)
    
    def evaluate(self, test_data, y_test):
        """Evaluate model performance on test data."""
        X_test, _ = self.feature_engineering(test_data, fit=False)
        preds = self.model.predict(X_test)
        print(classification_report(y_test, preds))
        return preds
    
    def detect_billing_pattern(self, group):
        """Identify recurring billing pattern from transaction intervals."""
        group = group.sort_values("date")
        
        if len(group) < 3:
            return None
        
        intervals = group["date"].diff().dt.days.dropna()
        
        # Reject if multiple transactions within 3 days (clusters)
        if (intervals <= 3).sum() >= 2:
            return None
        
        median_interval = intervals.median()
        best_pattern = None
        smallest_error = 999
        
        for name, days in self.cadence_days.items():
            error = abs(median_interval - days)
            if error < smallest_error:
                smallest_error = error
                best_pattern = name
        
        return best_pattern if smallest_error <= 10 else None
    
    def predict_next_billing(self, group, cadence):
        """Predict next billing date based on detected pattern."""
        last_date = group["date"].max()
        return last_date + pd.Timedelta(days=self.cadence_days[cadence])
    
    def subscription_status(self, next_billing, today):
        """Determine subscription status based on next billing date."""
        return "LIKELY CANCELLED" if next_billing < today else "ACTIVE"
    
    def analyze(self, testing_set):
        """Analyze stored test data and detect active subscriptions."""
        X_test, df_test = self.feature_engineering(testing_set, fit=False)
        df_test["pred_recurring"] = self.model.predict(X_test)
        
        recurring = df_test[df_test["pred_recurring"] == 1]
        today = df_test["date"].max()
        results = []
        
        for merchant, group in recurring.groupby("merchant"):
            group = group.sort_values("date")
            last_seen = group["date"].max()
            
            # Skip merchants inactive > 1 year
            if last_seen < today - pd.Timedelta(days=365):
                continue
            
            cadence = self.detect_billing_pattern(group)
            if cadence is None:
                continue
            
            next_billing = self.predict_next_billing(group, cadence)
            status = self.subscription_status(next_billing, today)
            annual_cost = group["debit"].mean() * (365 / self.cadence_days[cadence])
            subscription_age = (group["date"].max() - group["date"].min()).days
            
            results.append({
                "merchant": merchant,
                "transactions": len(group),
                "first_seen": group["date"].min(),
                "last_seen": last_seen,
                "avg_amount": round(group["debit"].mean(), 2),
                "cadence": cadence,
                "next_billing": next_billing,
                "status": status,
                "annual_cost": annual_cost,
                "subscription_age": subscription_age,
            })
        
        return pd.DataFrame(results).sort_values("next_billing").round(2)


# Usage
if __name__ == "__main__":
    testing_set = pd.read_csv("data/daniel_testing_set.csv")
    testing_set.rename(columns={"Date": "date", "Description": "description", "Debit": "debit"}, inplace=True)
    detector = SubscriptionDetector(testing_set)
    
    # Load and train
    training_set = detector.load_data("data/main_training_data.csv")
    detector.train(training_set)

    # Analyze and retrieve results
    results_df = detector.analyze()
    print(results_df)