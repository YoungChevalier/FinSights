from fastapi import APIRouter, HTTPException, Depends
from models.schemas import AnalyticsRequest, AnalyticsReport
from database import get_database
from routes.auth import verify_jwt
from services.ml_analytics import run_spending_analytics
import logging

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

@router.post("/spending", response_model=AnalyticsReport)
async def process_spending_analytics(request: AnalyticsRequest, user_id: str = Depends(verify_jwt)):
    """
    Ingests raw transaction data, runs Pandas aggregation, IsolationForest anomaly detection, 
    and Linear Regression prediction to generate gamified insights.
    """
    try:
        # Convert Pydantic models to dicts for pandas processing
        transactions_data = [txn.dict() for txn in request.transactions]
        
        # Run ML engine
        report_dict = run_spending_analytics(transactions_data)
        
        return AnalyticsReport(**report_dict)
        
    except Exception as e:
        logger.error(f"Error processing spending analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
