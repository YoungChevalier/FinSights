import uuid
from datetime import datetime, timedelta
import random

class MockAccountAggregator:
    @staticmethod
    def initiate_consent(user_id: str) -> dict:
        """
        Mocks the creation of a consent request on the AA side.
        Returns a consent ID and a URL for the user to approve the consent.
        """
        consent_id = str(uuid.uuid4())
        return {
            "consent_id": consent_id,
            "status": "PENDING",
            "consent_url": f"https://mock-aa-ui.local/consent/{consent_id}?user={user_id}"
        }

    @staticmethod
    def fetch_parsed_data(consent_id: str) -> list[dict]:
        """
        Mocks fetching the actual parsed data after consent is approved.
        Returns a list of transactions.
        """
        transactions = []
        categories = ["Food", "Transport", "Utilities", "Salary", "Entertainment", "Shopping", "Investment"]
        merchants = ["Zomato", "Uber", "Amazon", "Netflix", "Starbucks", "Dmart", "Zerodha"]
        
        # Generate some random transactions for the last 30 days
        now = datetime.utcnow()
        for i in range(50):
            days_ago = random.randint(0, 30)
            date = now - timedelta(days=days_ago)
            category = random.choice(categories)
            
            is_credit = category == "Salary" or (category == "Investment" and random.choice([True, False]))
            
            if category == "Salary":
                amount = random.randint(50000, 150000)
                merchant = "Employer Corp"
            else:
                amount = random.randint(100, 5000)
                merchant = random.choice(merchants)
            
            transactions.append({
                "txn_id": str(uuid.uuid4()),
                "date": date.isoformat(),
                "amount": float(amount),
                "type": "CREDIT" if is_credit else "DEBIT",
                "category": category,
                "merchant": merchant,
                "description": f"Payment to {merchant}" if not is_credit else f"Received from {merchant}"
            })
            
        return transactions
