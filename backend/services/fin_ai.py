import logging
from config import settings

logger = logging.getLogger(__name__)

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    logger.warning("google.generativeai is not installed. Fin-AI will run in mock mode.")

if HAS_GEMINI and settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

SYSTEM_PROMPT_TEMPLATE = """
You are "Fin-AI", a hyper-intelligent, slang-friendly, and highly relatable Gen Z finance expert. 
You use simple analogies, light humor, and avoid boring corporate jargon. Speak directly to the user.
Your goal is to explain concepts simply and offer personalized nudges.

Here is the user's current financial context:
- Name: {name}
- Level: {level} ({xp} XP)
- Weekly Savings: ₹{weekly_savings}
- Total Savings: ₹{total_savings}

Keep your responses concise, punchy, and formatted in markdown. Use emojis!
"""

async def generate_chat_response(message: str, user_profile: dict) -> str:
    """
    Constructs the prompt and calls the Gemini API.
    Falls back to a mock response if the API key is missing.
    """
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        name=user_profile.get("name", "Bestie"),
        level=user_profile.get("level", 1),
        xp=user_profile.get("xp", 0),
        weekly_savings=user_profile.get("weekly_savings", 0),
        total_savings=user_profile.get("total_savings", 0)
    )

    if not HAS_GEMINI or not settings.gemini_api_key:
        logger.info("Fin-AI: Using mock response due to missing API key or library.")
        return f"Hey {user_profile.get('name', 'there')}! 👋 Since my Gemini brain isn't hooked up yet (missing API key), I'll just say: Your ₹{user_profile.get('weekly_savings', 0)} weekly savings are looking super lit! 🔥 Keep investing and watch that compound interest pop off! 💸"

    try:
        # Use gemini-1.5-flash for fast chat responses
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Yikes, my brain is glitching right now! 😵 Try asking me again later."
