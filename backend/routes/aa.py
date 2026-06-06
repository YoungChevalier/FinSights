from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from config import settings
from database import get_database
from services.mock_aa import MockAccountAggregator
import logging

from routes.auth import verify_jwt

router = APIRouter(prefix="/api/consent", tags=["account_aggregator"])
logger = logging.getLogger(__name__)

@router.post("/init")
async def init_consent(user_id: str = Depends(verify_jwt)):
    try:
        # Generate consent URL
        consent_data = MockAccountAggregator.initiate_consent(user_id)
        
        # We could save the consent_id to DB as "PENDING", but for now just return it
        return {
            "message": "Consent request created successfully",
            "data": consent_data
        }
    except Exception as e:
        logger.error(f"Error initiating consent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

class FetchRequest(BaseModel):
    consent_id: str

@router.post("/fetch")
async def fetch_bank_data(request: FetchRequest, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        # Mock AA returns parsed transaction data
        transactions = MockAccountAggregator.fetch_parsed_data(request.consent_id)
        
        if not transactions:
            return {"message": "No transactions found", "count": 0}
            
        # Add user_id to all transactions for MongoDB storage
        for txn in transactions:
            txn["user_id"] = user_id
            
        # Store in MongoDB (using insert_many or upsert)
        # We will use update_one with upsert based on txn_id to avoid duplicates
        collection = db["transactions"]
        
        # Bulk write would be more efficient, but doing it in a loop for simplicity
        # Or just use insert_many if we assume fresh data, but upsert is safer
        # Let's just insert them all if we don't care about duplicates for this mock
        # Or better: delete existing for this consent_id and insert new
        
        from pymongo import UpdateOne
        operations = [
            UpdateOne(
                {"txn_id": txn["txn_id"]},
                {"$set": txn},
                upsert=True
            ) for txn in transactions
        ]
        
        if operations:
            await collection.bulk_write(operations)

        return {
            "message": "Bank data fetched and stored successfully",
            "count": len(transactions)
        }
    except Exception as e:
        logger.error(f"Error fetching bank data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
