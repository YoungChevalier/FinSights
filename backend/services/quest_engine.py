import logging
from datetime import datetime

logger = logging.getLogger(__name__)

QUEST_TEMPLATES = [
    {
        "quest_id": "q_no_spend_sat",
        "name": "No-Spend Saturday",
        "description": "Spend absolutely ₹0 on a Saturday to prove your discipline.",
        "rule_type": "spend_limit",
        "target_threshold": 0.0,
        "reward_xp": 150,
        "reward_coins": 500,
        "duration_days": 1
    },
    {
        "quest_id": "q_streak_saver",
        "name": "Streak Saver",
        "description": "Log into FinSights for 7 days in a row.",
        "rule_type": "streak",
        "target_threshold": 7.0,
        "reward_xp": 300,
        "reward_coins": 1000,
        "duration_days": 7
    },
    {
        "quest_id": "q_1k_week",
        "name": "₹1000 in a Week",
        "description": "Deposit at least ₹1000 into your savings account this week.",
        "rule_type": "savings_target",
        "target_threshold": 1000.0,
        "reward_xp": 250,
        "reward_coins": 800,
        "duration_days": 7
    },
    {
        "quest_id": "q_crypto_curious",
        "name": "Crypto Curious",
        "description": "Read the intro to Crypto article in the learn section.",
        "rule_type": "custom_action",
        "target_threshold": 1.0,
        "reward_xp": 100,
        "reward_coins": 250,
        "duration_days": 30
    },
    {
        "quest_id": "q_lock_it_up",
        "name": "Lock it Up",
        "description": "Use the Smart Lock feature to lock ₹5000 for 30 days.",
        "rule_type": "custom_action",
        "target_threshold": 1.0,
        "reward_xp": 500,
        "reward_coins": 2000,
        "duration_days": 30
    },
    {
        "quest_id": "q_fast_food_diet",
        "name": "Fast Food Diet",
        "description": "Spend less than ₹500 on Food/Dining this week.",
        "rule_type": "spend_limit",
        "target_threshold": 500.0,
        "reward_xp": 200,
        "reward_coins": 600,
        "duration_days": 7
    },
    {
        "quest_id": "q_early_bird",
        "name": "Early Bird Saver",
        "description": "Make a deposit before 9 AM.",
        "rule_type": "custom_action",
        "target_threshold": 1.0,
        "reward_xp": 100,
        "reward_coins": 300,
        "duration_days": 1
    },
    {
        "quest_id": "q_payday_planner",
        "name": "Payday Planner",
        "description": "Save 20% of your salary within 24 hours of receiving it.",
        "rule_type": "savings_target",
        "target_threshold": 1.0, # percentage abstraction
        "reward_xp": 600,
        "reward_coins": 2500,
        "duration_days": 1
    },
    {
        "quest_id": "q_diversification",
        "name": "Diversification",
        "description": "Invest in a new asset class (e.g. mutual funds).",
        "rule_type": "custom_action",
        "target_threshold": 1.0,
        "reward_xp": 400,
        "reward_coins": 1500,
        "duration_days": 30
    },
    {
        "quest_id": "q_level_10_legend",
        "name": "Level 10 Legend",
        "description": "Reach Level 10 in FinSights.",
        "rule_type": "level_target",
        "target_threshold": 10.0,
        "reward_xp": 1000,
        "reward_coins": 5000,
        "duration_days": 365
    }
]

async def seed_quests(db):
    """Inserts the 10 static templates into the quests collection if empty."""
    col = db["quest_templates"]
    count = await col.count_documents({})
    if count == 0:
        await col.insert_many(QUEST_TEMPLATES)
        logger.info("Successfully seeded 10 quest templates into MongoDB.")

async def evaluate_user_quests(db, user_id: str):
    """
    Simulates a daily background job.
    Scans all 'active' UserQuests for this user, evaluates their condition against
    current stats, and marks them 'completed' while awarding XP/Coins if threshold met.
    """
    user_col = db["users"]
    user = await user_col.find_one({"user_id": user_id})
    if not user:
        return
        
    active_quests = user.get("active_quests", [])
    completed_quests = user.get("completed_quests", [])
    
    # We will simulate evaluation based on 'streak_count' and 'total_savings'
    current_streak = user.get("streak_count", 0)
    total_savings = user.get("total_savings", 0.0)
    current_level = user.get("level", 1)
    
    new_active = []
    new_completed = completed_quests
    xp_to_add = 0
    coins_to_add = 0
    notifications = []
    
    for q in active_quests:
        quest_id = q.get("quest_id")
        template = next((t for t in QUEST_TEMPLATES if t["quest_id"] == quest_id), None)
        
        if not template:
            new_active.append(q)
            continue
            
        is_completed = False
        new_progress = q.get("current_progress", 0.0)
        
        # Rule Evaluation Engine
        if template["rule_type"] == "streak":
            new_progress = float(current_streak)
            if new_progress >= template["target_threshold"]:
                is_completed = True
                
        elif template["rule_type"] == "savings_target":
            # For a mock, just check total_savings
            new_progress = float(total_savings)
            if new_progress >= template["target_threshold"]:
                is_completed = True
                
        elif template["rule_type"] == "level_target":
            new_progress = float(current_level)
            if new_progress >= template["target_threshold"]:
                is_completed = True
                
        else:
            # Custom actions/spend limits would require parsing actual transactions via the ML module.
            # We mock progress for testing.
            pass

        if is_completed:
            q["status"] = "completed"
            q["current_progress"] = new_progress
            new_completed.append(q)
            xp_to_add += template["reward_xp"]
            coins_to_add += template["reward_coins"]
            notifications.append(f"Quest Completed: {template['name']}! Earned {template['reward_xp']} XP & 🪙 {template['reward_coins']}.")
        else:
            q["current_progress"] = new_progress
            new_active.append(q)
            
    # Apply rewards if any
    if xp_to_add > 0 or coins_to_add > 0:
        await user_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "active_quests": new_active,
                    "completed_quests": new_completed,
                },
                "$inc": {
                    "xp": xp_to_add,
                    "coins": coins_to_add
                }
            }
        )
        # Note: You would also recalculate Level here via services/gamification.py
        
    return {
        "completed_count": len(new_completed) - len(completed_quests),
        "notifications": notifications,
        "xp_awarded": xp_to_add,
        "coins_awarded": coins_to_add
    }
