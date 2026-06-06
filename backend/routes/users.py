from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from database import get_database
from models.schemas import UserCreate, UserProfile
from routes.auth import verify_jwt
import logging

router = APIRouter(prefix="/api/users", tags=["users"])
logger = logging.getLogger(__name__)

@router.post("")
async def create_user(user_data: UserCreate, db = Depends(get_database)):
    try:
        collection = db["users"]
        existing = await collection.find_one({"user_id": user_data.user_id})
        
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
            
        new_profile = UserProfile(**user_data.dict())
        profile_dict = new_profile.dict()
        
        await collection.insert_one(profile_dict)
        
        # Remove MongoDB ObjectId for response
        if "_id" in profile_dict:
            del profile_dict["_id"]
            
        return profile_dict
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}")
async def get_user(user_id: str, db = Depends(get_database)):
    try:
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if "_id" in user:
            del user["_id"]
            
        return user
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
