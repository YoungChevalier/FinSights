from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import auth, credentials
from config import settings
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# Try to initialize firebase admin app (requires GOOGLE_APPLICATION_CREDENTIALS or similar)
# For local dev without creds, we can mock it if needed.
try:
    firebase_admin.get_app()
except ValueError:
    try:
        firebase_admin.initialize_app()
        logger.info("Firebase Admin initialized.")
    except Exception as e:
        logger.warning(f"Could not initialize Firebase Admin SDK: {e}")

class LoginRequest(BaseModel):
    firebase_id_token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        # In a real app, verify with Firebase:
        # decoded_token = auth.verify_id_token(request.firebase_id_token)
        # user_id = decoded_token['uid']
        # phone_number = decoded_token.get('phone_number')
        
        # MOCK FOR DEVELOPMENT:
        # Since we might not have Firebase setup locally yet, if the token starts with "mock_", accept it
        if request.firebase_id_token.startswith("mock_"):
            user_id = request.firebase_id_token.replace("mock_", "")
            phone_number = "+1234567890"
        else:
            # Attempt real verification
            try:
                decoded_token = auth.verify_id_token(request.firebase_id_token)
                user_id = decoded_token['uid']
                phone_number = decoded_token.get('phone_number', '')
            except Exception as e:
                logger.error(f"Firebase token verification failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid Firebase ID token")

        # Create session JWT
        jwt_data = {"sub": user_id, "phone": phone_number}
        access_token = create_access_token(jwt_data)
        
        return {"access_token": access_token}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
