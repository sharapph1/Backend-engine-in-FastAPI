from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, daily_usage, game, referral, streak

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.APP_NAME
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(streak.router, prefix="/api/v1")
app.include_router(referral.router, prefix="/api/v1")
app.include_router(game.router, prefix="/api/v1")
app.include_router(daily_usage.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} Backend 🚀",
        "version": "1.0.0",
        "docs_url": "/docs",
    }