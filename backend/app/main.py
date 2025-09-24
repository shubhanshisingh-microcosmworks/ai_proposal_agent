from fastapi import FastAPI
from .core.config import settings
from .core.database import client, create_db_indexes
from .api.v1.endpoints.users import router as users_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

@app.on_event("startup")
async def startup_db_client():
    print("Connecting to MongoDB...")
    await create_db_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Disconnecting from MongoDB...")
    client.close()

app.include_router(users_router, tags=["Users"], prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Proposal Agent API is running!"}