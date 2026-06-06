from datetime import datetime

# Level thresholds for XP
# e.g. Level 1: 0-499, Level 2: 500-1499, Level 3: 1500-2999
LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 500),
    (3, 1500),
    (4, 3000),
    (5, 5000),
    (6, 7500),
    (7, 10000),
    (8, 15000),
    (9, 20000),
    (10, 30000)
]

def calculate_level(xp: int) -> int:
    current_level = 1
    for level, threshold in LEVEL_THRESHOLDS:
        if xp >= threshold:
            current_level = level
        else:
            break
    return current_level

def calculate_level_up_bonus(old_level: int, new_level: int) -> int:
    """Returns coins awarded for leveling up"""
    if new_level > old_level:
        # e.g. 50 coins per level gained
        return (new_level - old_level) * 50
    return 0

def process_streak(last_checkin: datetime, current_time: datetime) -> tuple[int, int, bool]:
    """
    Returns (new_streak_count, bonus_xp, streak_reset_boolean)
    """
    if not last_checkin:
        return 1, 0, False # First checkin
        
    delta_days = (current_time.date() - last_checkin.date()).days
    
    if delta_days == 0:
        # Already checked in today
        return -1, 0, False
        
    if delta_days == 1:
        # Consecutive day
        return 1, 0, False # We will add this 1 to current streak
    
    # delta_days > 1: Streak broken
    return 1, 0, True # Reset to 1

def calculate_streak_bonus(new_streak: int) -> int:
    bonus = 0
    if new_streak == 7:
        bonus = 100
    elif new_streak == 30:
        bonus = 500
    elif new_streak % 30 == 0:
        bonus = 500
    elif new_streak % 7 == 0:
        bonus = 100
    return bonus

def check_milestones(total_savings: float) -> list[str]:
    milestones_unlocked = []
    if total_savings >= 5000 and total_savings < 6000:
        milestones_unlocked.append('Unlocked: Cyber Tower District')
    elif total_savings >= 15000 and total_savings < 16000:
        milestones_unlocked.append('Unlocked: Neon Markets')
    return milestones_unlocked

