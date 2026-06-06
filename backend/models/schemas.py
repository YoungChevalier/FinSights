from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str
    name: str
    college: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    college: Optional[str] = None
    avatar_url: Optional[str] = None
    level: int = 1
    xp: int = 0
    coins: int = 0
    streak: int = 0
    total_savings: float = 0.0
    weekly_savings: float = 0.0
    last_checkin_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DepositRequest(BaseModel):
    amount: float

class DepositResponse(BaseModel):
    message: str
    xp_gained: int
    new_level: int
    level_up_occurred: bool
    coins_awarded: int
    updated_profile: dict

class CheckinResponse(BaseModel):
    message: str
    streak_count: int
    bonus_xp: int
    streak_reset: bool

class TransactionItem(BaseModel):
    txn_id: str
    amount: float
    type: str
    category: str
    merchant: str
    description: str

class WebhookPayload(BaseModel):
    user_id: str
    consent_id: str
    transactions: list[TransactionItem]

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


class AnomalyItem(BaseModel):
    txn_id: str
    amount: float
    reason: str

class AnalyticsRequest(BaseModel):
    transactions: list[TransactionItem]

class AnalyticsReport(BaseModel):
    top_spend_category: str
    weekend_heavy: bool
    predicted_monthly_spend: float
    anomalies: list[AnomalyItem]
    suggested_quest: str


class AffiliateOffer(BaseModel):
    offer_id: str
    name: str
    interest_rate: Optional[str] = None
    cta_url: str
    commission_tier: str
    description: str

class ConversionEvent(BaseModel):
    offer_id: str

class ShopItem(BaseModel):
    item_id: str
    name: str
    coin_price: int
    real_money_price_inr: int
    theme_type: str

class PurchaseRequest(BaseModel):
    item_id: str


class QuestTemplate(BaseModel):
    quest_id: str
    name: str
    description: str
    rule_type: str # 'spend_limit', 'streak', 'savings_target', 'custom_action'
    target_threshold: float
    reward_xp: int
    reward_coins: int
    duration_days: int

class UserQuest(BaseModel):
    quest_id: str
    status: str # 'active', 'completed'
    current_progress: float
    target_threshold: float
    accepted_at: str

class QuestAcceptRequest(BaseModel):
    quest_id: str

