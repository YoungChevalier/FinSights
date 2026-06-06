from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse
from database import get_database
from routes.auth import verify_jwt
from services.fin_ai import generate_chat_response
import logging

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ChatResponse)
async def chat_with_fin_ai(request: ChatRequest, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Call the Gemini service
        ai_reply = await generate_chat_response(request.message, user)
        
        return ChatResponse(reply=ai_reply)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
