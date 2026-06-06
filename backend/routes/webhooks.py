from fastapi import APIRouter, HTTPException, Depends
from models.schemas import WebhookPayload
from database import get_database
from services.gamification import calculate_level, calculate_level_up_bonus, check_milestones
from services.fcm import send_push_notification
import logging

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/aa")
async def handle_aa_webhook(payload: WebhookPayload, db = Depends(get_database)):
    """
    Webhook receiver for Account Aggregator real-time transaction sync.
    Filters out noise and calculates XP.
    """
    try:
        user_id = payload.user_id
        collection = db["users"]
        user = await collection.find_one({"user_id": user_id})
        
        if not user:
            logger.warning(f"Webhook received for unknown user: {user_id}")
            return {"status": "ignored", "reason": "user not found"}

        savings_deposits = []
        
        # 1. Parsing & Classification
        for txn in payload.transactions:
            # Heuristic filter: only CREDITs, and skip obvious non-savings like refunds or small transfers
            # In a real app, this logic would be much more sophisticated (ML-based or MCC-based)
            if txn.type == "CREDIT":
                if txn.category in ["Transfer In", "Investment", "Salary"]:
                    savings_deposits.append(txn)
                    
        if not savings_deposits:
            return {"status": "processed", "message": "No savings transactions found"}
            
        total_deposit_amount = sum(txn.amount for txn in savings_deposits)
        
        # 2. Gamification XP processing
        xp_gained = int(total_deposit_amount)
        old_level = user.get("level", 1)
        new_xp = user.get("xp", 0) + xp_gained
        new_total_savings = user.get("total_savings", 0.0) + total_deposit_amount
        new_weekly_savings = user.get("weekly_savings", 0.0) + total_deposit_amount
        
        new_level = calculate_level(new_xp)
        coins_awarded = calculate_level_up_bonus(old_level, new_level)
        new_coins = user.get("coins", 0) + coins_awarded
        
        # Check city milestones
        unlocked_milestones = check_milestones(new_total_savings)
        
        # Update DB
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "xp": new_xp,
                "level": new_level,
                "total_savings": new_total_savings,
                "weekly_savings": new_weekly_savings,
                "coins": new_coins
            }}
        )
        
        # 3. Push Notification (FCM)
        notification_title = "Cha-Ching! Savings Detected 🚀"
        notification_body = f"Your ₹{total_deposit_amount:,.2f} deposit just earned you {xp_gained} XP!"
        
        if unlocked_milestones:
            notification_body += f" 🎉 You {unlocked_milestones[0]}!"
            
        send_push_notification(user_id, notification_title, notification_body)
        
        return {"status": "success", "xp_awarded": xp_gained, "milestones": unlocked_milestones}
        
    except Exception as e:
        logger.error(f"Error processing AA webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/test_trigger")
async def trigger_test_webhook(user_id: str, amount: float, db = Depends(get_database)):
    """
    Mock trigger to simulate a real bank event locally.
    """
    import uuid
    mock_payload = WebhookPayload(
        user_id=user_id,
        consent_id="test_consent_123",
        transactions=[
            {
                "txn_id": str(uuid.uuid4()),
                "amount": amount,
                "type": "CREDIT",
                "category": "Investment",
                "merchant": "Groww",
                "description": "SIP Transfer"
            }
        ]
    )
    return await handle_aa_webhook(mock_payload, db=db)
