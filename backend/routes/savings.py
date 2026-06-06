from fastapi import APIRouter, HTTPException, Depends
from database import get_database
from models.schemas import DepositRequest, DepositResponse
from routes.auth import verify_jwt
from services.gamification import calculate_level, calculate_level_up_bonus
import logging

router = APIRouter(prefix="/api/savings", tags=["savings"])
logger = logging.getLogger(__name__)

@router.post("/deposit", response_model=DepositResponse)
async def record_deposit(request: DepositRequest, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Deposit amount must be positive")
            
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # 1 XP = 1 Rupee
        xp_gained = int(request.amount)
        
        old_level = user.get("level", 1)
        new_xp = user.get("xp", 0) + xp_gained
        new_total_savings = user.get("total_savings", 0.0) + request.amount
        new_weekly_savings = user.get("weekly_savings", 0.0) + request.amount
        
        # Check level up
        new_level = calculate_level(new_xp)
        level_up_occurred = new_level > old_level
        coins_awarded = calculate_level_up_bonus(old_level, new_level)
        new_coins = user.get("coins", 0) + coins_awarded
        
        # Update DB
        update_data = {
            "xp": new_xp,
            "level": new_level,
            "total_savings": new_total_savings,
            "weekly_savings": new_weekly_savings,
            "coins": new_coins
        }
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Fetch updated user for response
        updated_user = await collection.find_one({"user_id": user_id})
        if "_id" in updated_user:
            del updated_user["_id"]
            
        return DepositResponse(
            message="Deposit recorded successfully",
            xp_gained=xp_gained,
            new_level=new_level,
            level_up_occurred=level_up_occurred,
            coins_awarded=coins_awarded,
            updated_profile=updated_user
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing deposit: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
