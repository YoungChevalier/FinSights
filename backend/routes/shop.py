from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ShopItem, PurchaseRequest
from database import get_database
from routes.auth import verify_jwt
import logging

router = APIRouter(prefix="/api/shop", tags=["shop"])
logger = logging.getLogger(__name__)

# Static catalog of Cosmetic Virtual Asset Packs
SHOP_CATALOG = [
    {
        "item_id": "theme_cyberpunk_01",
        "name": "Cyberpunk Neon City",
        "coin_price": 2500,
        "real_money_price_inr": 99,
        "theme_type": "city_theme"
    },
    {
        "item_id": "theme_retro_01",
        "name": "Retro 80s Synthwave",
        "coin_price": 1000,
        "real_money_price_inr": 49,
        "theme_type": "city_theme"
    },
    {
        "item_id": "theme_forest_01",
        "name": "Zen Forest Retreat",
        "coin_price": 500,
        "real_money_price_inr": 29,
        "theme_type": "city_theme"
    }
]

@router.get("/items", response_model=list[ShopItem])
async def get_shop_items():
    return [ShopItem(**item) for item in SHOP_CATALOG]

@router.post("/purchase")
async def purchase_item(request: PurchaseRequest, user_id: str = Depends(verify_jwt), db = Depends(get_database)):
    try:
        # 1. Validate Item Exists
        item = next((i for i in SHOP_CATALOG if i["item_id"] == request.item_id), None)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in catalog")
            
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        current_coins = user.get("coins", 0)
        unlocked_themes = user.get("unlocked_themes", [])
        
        # 2. Check if already owned
        if request.item_id in unlocked_themes:
            raise HTTPException(status_code=400, detail="You already own this cosmetic item!")
            
        # 3. Check coin balance
        if current_coins < item["coin_price"]:
            raise HTTPException(status_code=400, detail="Insufficient coins. Play more to save up!")
            
        # 4. Process Purchase (Atomic Update)
        new_balance = current_coins - item["coin_price"]
        
        await collection.update_one(
            {"user_id": user_id},
            {
                "$set": {"coins": new_balance},
                "$push": {"unlocked_themes": request.item_id}
            }
        )
        
        logger.info(f"Shop Purchase Successful: User {user_id} bought {request.item_id} for {item['coin_price']} coins.")
        
        return {
            "status": "success", 
            "message": f"Successfully unlocked {item['name']}!",
            "new_coin_balance": new_balance
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing shop purchase: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
