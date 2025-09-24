# backend/app/api/v1/endpoints/users.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserCreate, UserInDB, UserUpdate, Profile, Education, Experience, Project, Skill, PasswordChange
from ....core.security import hash_password, verify_password, create_access_token
from ....core.database import users_collection
from bson import ObjectId
from ....core.dependencies import get_current_user
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Register a new user.
    """
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    hashed_password = hash_password(user.password)
    
    # 🐛 FIXED: Create a dictionary for the data to be inserted
    user_data = {
        "email": user.email,
        "password_hash": hashed_password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "role": "freelancer", # Default role
        "is_active": True, # Default status
        "is_deleted": False # Default soft-delete status
    }

    new_user = await users_collection.insert_one(user_data)
    
    # 🐛 FIXED: Find the newly created user by its inserted_id
    created_user = await users_collection.find_one({"_id": new_user.inserted_id})
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve newly created user"
        )
        
    return UserInDB.model_validate(created_user)

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a JWT access token.
    """
    user = await users_collection.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def get_my_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the full profile of the current authenticated user.
    """
    return current_user

@router.patch("/me", response_model=UserInDB)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update the authenticated user's profile, including nested data.
    """
    update_data = {}
    
    if user_update.first_name is not None:
        update_data["first_name"] = user_update.first_name
    if user_update.last_name is not None:
        update_data["last_name"] = user_update.last_name
    if user_update.phone_number is not None:
        update_data["phone_number"] = user_update.phone_number
    if user_update.org_id is not None:
        update_data["org_id"] = user_update.org_id
    if user_update.role is not None:
        update_data["role"] = user_update.role
    
    if user_update.profile is not None:
        update_data["profile"] = user_update.profile.model_dump()
        
    if user_update.education is not None:
        update_data["education"] = [item.model_dump() for item in user_update.education]
    if user_update.experience is not None:
        update_data["experience"] = [item.model_dump() for item in user_update.experience]
    if user_update.projects is not None:
        update_data["projects"] = [item.model_dump() for item in user_update.projects]
    if user_update.skills is not None:
        update_data["skills"] = [item.model_dump() for item in user_update.skills]
    
    if user_update.is_deleted is not None:
        update_data["is_deleted"] = user_update.is_deleted

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update provided"
        )
    
    result = await users_collection.update_one(
        {"email": current_user.email},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for update"
        )
      
    updated_user_dict = current_user.model_dump(by_alias=True, exclude_unset=True)
    updated_user_dict.update(update_data)
    
    return UserInDB.model_validate(updated_user_dict)

@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    password_change_form: PasswordChange,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Change the authenticated user's password.
    """

    new_password = password_change_form.new_password
    
    hashed_password = hash_password(new_password)
    await users_collection.update_one(
        {"email": current_user.email},
        {"$set": {"password_hash": hashed_password}}
    )
    
    return