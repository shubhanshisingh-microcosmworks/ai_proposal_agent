from fastapi import APIRouter

# Import the individual routers
from .endpoints.users import router as users_router
from .endpoints.organizations import router as orgs_router

# Create main v1 router
api_router = APIRouter()

# Include the individual routers
api_router.include_router(users_router, tags=["Users"], prefix="/endpoints/users")
api_router.include_router(orgs_router, tags=["Organizations"], prefix="/endpoints/organizations")


__all__ = ["api_router"]