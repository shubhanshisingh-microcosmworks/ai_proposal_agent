# backend/app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, TEXT
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_database()

# Database collections
users_collection = db.users
organizations_collection = db.organizations
jobs_collection = db.jobs
proposals_collection = db.proposals
resumes_collection = db.resumes

# Create unique index for the 'users' collection
async def create_db_indexes():
    """
    Creates necessary indexes on application startup.
    """
    await users_collection.create_index(
        [("email", ASCENDING)],
        unique=True
    )
    print("MongoDB indexes created successfully.")