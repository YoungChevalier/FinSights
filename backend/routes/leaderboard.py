from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from database import get_database
import logging

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])
logger = logging.getLogger(__name__)

@router.get("")
async def get_leaderboard(college: Optional[str] = None, limit: int = 20, db = Depends(get_database)):
    try:
        collection = db["users"]
        query = {}
        if college:
            # Case-insensitive partial match or exact match depending on needs
            query["college"] = {"$regex": f"^{college}$", "$options": "i"}
            
        # Sort descending by weekly_savings
        cursor = collection.find(query).sort("weekly_savings", -1).limit(limit)
        
        users = await cursor.to_list(length=limit)
        
        leaderboard = []
        for rank, user in enumerate(users, start=1):
            leaderboard.append({
                "rank": rank,
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "avatar_url": user.get("avatar_url"),
                "level": user.get("level", 1),
                "weekly_savings": user.get("weekly_savings", 0.0),
                "college": user.get("college")
            })
            
        return {"leaderboard": leaderboard}
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
