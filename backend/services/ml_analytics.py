import logging
import numpy as np
try:
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    from sklearn.linear_model import LinearRegression
    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False

logger = logging.getLogger(__name__)

def run_spending_analytics(transactions_data: list[dict]) -> dict:
    """
    Runs ML analytics on a list of transaction dictionaries.
    Expected dict format: { "txn_id": str, "date": iso_string, "amount": float, "category": str, "merchant": str }
    """
    if not HAS_ML_DEPS:
        logger.warning("ML dependencies not found. Returning mock analytics.")
        return {
            "top_spend_category": "Food",
            "weekend_heavy": True,
            "predicted_monthly_spend": 10000.0,
            "anomalies": [{"txn_id": "mock_txn", "amount": 5000, "reason": "ML deps missing"}],
            "suggested_quest": "No-Spend Saturday Quest"
        }

    if not transactions_data:
        return {
            "top_spend_category": "None",
            "weekend_heavy": False,
            "predicted_monthly_spend": 0.0,
            "anomalies": [],
            "suggested_quest": "Make your first transaction!"
        }

    try:
        df = pd.DataFrame(transactions_data)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek # Monday=0, Sunday=6
        df['month'] = df['date'].dt.month
        df['year_month'] = df['date'].dt.to_period('M')
        
        # 1. Top Category
        top_category = df.groupby('category')['amount'].sum().idxmax()
        
        # 2. Weekend Heavy Detection
        weekend_df = df[df['day_of_week'].isin([5, 6])] # Sat, Sun
        weekday_df = df[df['day_of_week'].isin([0, 1, 2, 3, 4])]
        
        avg_weekend_spend = weekend_df['amount'].sum() / 2 if not weekend_df.empty else 0
        avg_weekday_spend = weekday_df['amount'].sum() / 5 if not weekday_df.empty else 0
        
        # Flag if weekend daily average is >40% higher than weekday daily average
        weekend_heavy = False
        if avg_weekday_spend > 0 and (avg_weekend_spend > 1.4 * avg_weekday_spend):
            weekend_heavy = True
        elif avg_weekday_spend == 0 and avg_weekend_spend > 0:
            weekend_heavy = True
            
        # 3. Anomaly Detection (Isolation Forest)
        anomalies = []
        if len(df) > 5:
            # We need sufficient data points for IsolationForest
            X = df[['amount']].values
            clf = IsolationForest(contamination=0.05, random_state=42)
            preds = clf.fit_predict(X)
            
            anomaly_indices = np.where(preds == -1)[0]
            avg_spend = df['amount'].mean()
            
            for idx in anomaly_indices:
                row = df.iloc[idx]
                if row['amount'] > avg_spend: # Only flag abnormally HIGH spends
                    anomalies.append({
                        "txn_id": row.get('txn_id', str(idx)),
                        "amount": float(row['amount']),
                        "reason": f"Anomaly detected by IsolationForest. Avg is ₹{avg_spend:.2f}"
                    })

        # 4. Predictive Modeling (Linear Regression)
        # Group by year_month to get monthly totals
        monthly_spend = df.groupby('year_month')['amount'].sum().reset_index()
        monthly_spend['time_index'] = np.arange(len(monthly_spend))
        
        predicted_spend = 0.0
        if len(monthly_spend) >= 3:
            # Predict next month
            X_train = monthly_spend[['time_index']].values
            y_train = monthly_spend['amount'].values
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            next_month_idx = np.array([[len(monthly_spend)]])
            pred = model.predict(next_month_idx)
            predicted_spend = max(0.0, float(pred[0]))
        else:
            # Not enough data, just use average
            predicted_spend = float(monthly_spend['amount'].mean()) if not monthly_spend.empty else 0.0

        # 5. Gamified Quest Generation
        suggested_quest = "Keep it up! Consistent Saver Quest"
        if weekend_heavy:
            suggested_quest = "No-Spend Saturday Quest"
        elif top_category == "Food" or top_category == "Dining":
            suggested_quest = "Cook at Home Challenge"
        elif len(anomalies) > 0:
            suggested_quest = "Budget Lockdown Quest"
            
        return {
            "top_spend_category": top_category,
            "weekend_heavy": weekend_heavy,
            "predicted_monthly_spend": round(predicted_spend, 2),
            "anomalies": anomalies,
            "suggested_quest": suggested_quest
        }

    except Exception as e:
        logger.error(f"Error during ML analytics processing: {e}")
        # Fallback due to parse/processing error
        return {
            "top_spend_category": "Unknown",
            "weekend_heavy": False,
            "predicted_monthly_spend": 0.0,
            "anomalies": [],
            "suggested_quest": "Analyze Your Spends Quest"
        }
