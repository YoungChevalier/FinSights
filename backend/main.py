import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import close_mongo_connection
from routes import auth, aa, users, savings, leaderboard, streak, webhooks, chat, analytics, affiliate, shop, quests

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FinSights API", description="Authentication and Bank Data Integration API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(aa.router)
app.include_router(users.router)
app.include_router(savings.router)
app.include_router(leaderboard.router)
app.include_router(streak.router)
app.include_router(webhooks.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(affiliate.router)
app.include_router(shop.router)
app.include_router(quests.router)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FinSights API is running"}
