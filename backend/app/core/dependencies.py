# backend/app/api/v1/dependencies.py

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from .security import decode_access_token
from .database import users_collection
from ..api.v1.models.user import UserInDB
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        user_email = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        
    except (JWTError, ValidationError):
        raise credentials_exception

    user_in_db = await users_collection.find_one({"email": user_email})
    if user_in_db is None:
        raise credentials_exception
    
    return UserInDB.model_validate(user_in_db)