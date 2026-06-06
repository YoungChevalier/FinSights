from fastapi import APIRouter, HTTPException, Depends
from models.schemas import AffiliateOffer, ConversionEvent
from database import get_database
from routes.auth import verify_jwt
import logging
from datetime import datetime

router = APIRouter(prefix="/api/affiliate", tags=["affiliate"])
logger = logging.getLogger(__name__)

# Mock database of partner offers
PARTNER_OFFERS = [
    {
        "offer_id": "hdfc_high_yield_1",
        "name": "HDFC High-Yield Savings Account",
        "interest_rate": "7.0% p.a.",
        "cta_url": "https://partner.hdfcbank.com/apply?ref=finsights",
        "commission_tier": "Tier 1 (₹500 CPA)",
        "description": "Unlock premium interest rates explicitly for top savers!"
    },
    {
        "offer_id": "zerodha_sip_1",
        "name": "Zerodha Smart SIP",
        "interest_rate": "Market Linked",
        "cta_url": "https://zerodha.com/open-account?c=finsights",
        "commission_tier": "Tier 2 (₹300 CPA)",
        "description": "Start your investment journey with zero brokerage on mutual funds."
    }
]

@router.get("/offers", response_model=list[AffiliateOffer])
async def get_affiliate_offers(user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        level = user.get("level", 1)
        total_savings = user.get("total_savings", 0.0)
        
        # CPA Trigger Condition: Level >= 5 OR Savings >= ₹5000
        if level >= 5 or total_savings >= 5000.0:
            return [AffiliateOffer(**offer) for offer in PARTNER_OFFERS]
            
        # Return empty if conditions not met
        return []
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching affiliate offers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/conversion")
async def track_conversion(event: ConversionEvent, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        collection = db["conversions"]
        
        conversion_doc = {
            "user_id": user_id,
            "offer_id": event.offer_id,
            "timestamp": datetime.utcnow()
        }
        
        await collection.insert_one(conversion_doc)
        logger.info(f"CPA Conversion Logged: User {user_id} -> Offer {event.offer_id}")
        
        return {"status": "success", "message": "Conversion tracked successfully"}
        
    except Exception as e:
        logger.error(f"Error tracking conversion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
