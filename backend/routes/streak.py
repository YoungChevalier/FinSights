from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from database import get_database
from models.schemas import CheckinResponse
from routes.auth import verify_jwt
from services.gamification import process_streak, calculate_streak_bonus
import logging

router = APIRouter(prefix="/api/streak", tags=["streak"])
logger = logging.getLogger(__name__)

@router.post("/checkin", response_model=CheckinResponse)
async def record_checkin(user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        current_time = datetime.utcnow()
        last_checkin = user.get("last_checkin_date")
        current_streak = user.get("streak", 0)
        
        # Process streak logic
        streak_modifier, bonus_xp, streak_reset = process_streak(last_checkin, current_time)
        
        if streak_modifier == -1:
            return CheckinResponse(
                message="Already checked in today",
                streak_count=current_streak,
                bonus_xp=0,
                streak_reset=False
            )
            
        if streak_reset:
            new_streak = 1
        else:
            new_streak = current_streak + streak_modifier
            
        # Check for milestone bonuses
        gained_bonus_xp = calculate_streak_bonus(new_streak)
        new_total_xp = user.get("xp", 0) + gained_bonus_xp
        
        # Update DB
        update_data = {
            "streak": new_streak,
            "last_checkin_date": current_time,
        }
        
        if gained_bonus_xp > 0:
            update_data["xp"] = new_total_xp
            # Could also trigger level up check here if needed, but keeping it simple for now
            
        await collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return CheckinResponse(
            message="Check-in successful",
            streak_count=new_streak,
            bonus_xp=gained_bonus_xp,
            streak_reset=streak_reset
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing check-in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
