from fastapi import APIRouter, HTTPException, Depends
from models.schemas import QuestTemplate, UserQuest, QuestAcceptRequest
from database import get_database
from routes.auth import verify_jwt
from services.quest_engine import seed_quests, evaluate_user_quests, QUEST_TEMPLATES
import logging
from datetime import datetime

router = APIRouter(prefix="/api/quests", tags=["quests"])
logger = logging.getLogger(__name__)

@router.on_event("startup")
async def startup_event():
    db = await get_database()
    await seed_quests(db)

@router.get("/active")
async def get_active_quests(user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    """Returns active, completed, and suggested quests for the UI."""
    try:
        user_col = db["users"]
        user = await user_col.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        active_quests = user.get("active_quests", [])
        completed_quests = user.get("completed_quests", [])
        
        # Determine active IDs to filter suggestions
        active_ids = [q["quest_id"] for q in active_quests] + [q["quest_id"] for q in completed_quests]
        
        # Generate Suggested Quests (mocked based on what's not accepted yet)
        suggested_quests = [q for q in QUEST_TEMPLATES if q["quest_id"] not in active_ids][:3]
        
        return {
            "active": active_quests,
            "completed": completed_quests,
            "suggested": suggested_quests
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching quests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{quest_id}/accept")
async def accept_quest(quest_id: str, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        template = next((t for t in QUEST_TEMPLATES if t["quest_id"] == quest_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Quest template not found")
            
        user_col = db["users"]
        user = await user_col.find_one({"user_id": user_id})
        
        # Check if already active
        active_quests = user.get("active_quests", [])
        if any(q["quest_id"] == quest_id for q in active_quests):
            raise HTTPException(status_code=400, detail="Quest already accepted")
            
        new_quest = {
            "quest_id": quest_id,
            "name": template["name"],
            "description": template["description"],
            "status": "active",
            "current_progress": 0.0,
            "target_threshold": template["target_threshold"],
            "reward_xp": template["reward_xp"],
            "reward_coins": template["reward_coins"],
            "accepted_at": datetime.utcnow().isoformat()
        }
        
        await user_col.update_one(
            {"user_id": user_id},
            {"$push": {"active_quests": new_quest}}
        )
        
        return {"status": "success", "message": f"Accepted quest: {template['name']}"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error accepting quest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/run-daily-evaluation")
async def trigger_daily_evaluation(user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    """
    Simulates the background CRON job that evaluates quest completion.
    In production, this would scan all users asynchronously.
    """
    try:
        result = await evaluate_user_quests(db, user_id)
        return {"status": "success", "evaluation_result": result}
    except Exception as e:
        logger.error(f"Error during quest evaluation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
