from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from ....core.database import organizations_collection, users_collection
from ..models.organization import OrganizationCreate, OrganizationInDB, OrganizationUpdate
from ..models.user import UserInDB
from ....core.dependencies import get_current_user
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=OrganizationInDB, status_code=status.HTTP_201_CREATED)
async def register_organization(organization: OrganizationCreate):
    """
    Register a new organization.
    """
    existing_org = await organizations_collection.find_one({"name": organization.name})
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization with this name already exists"
        )
    
    org_data = {
        "name": organization.name,
        "description": organization.description,
        "org_email": organization.org_email,
        "org_phone_number": organization.org_phone_number,
        "industry": organization.industry,
        "location": organization.location
    }

    new_org = await organizations_collection.insert_one(org_data)
    
    created_org = await organizations_collection.find_one({"_id": new_org.inserted_id})
    if created_org is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve newly created organization"
        )

    return OrganizationInDB.model_validate(created_org)


@router.get("/{org_id}", response_model=OrganizationInDB)
async def get_organization(org_id: str):
    """
    Get a specific organization by its ID.
    """
    if not ObjectId.is_valid(org_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Organization ID")

    org = await organizations_collection.find_one({"_id": ObjectId(org_id)})
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return OrganizationInDB.model_validate(org)


@router.patch("/{org_id}", response_model=OrganizationInDB)
async def update_organization(
    org_id: str,
    org_update: OrganizationUpdate, 
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an organization's details.
    """
    if not ObjectId.is_valid(org_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Organization ID")

    if not current_user.org_id == org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this organization."
        )
    
    update_data = org_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update provided"
        )
    
    result = await organizations_collection.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    updated_org = await organizations_collection.find_one({"_id": ObjectId(org_id)})
    if updated_org is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated organization"
        )
    
    return OrganizationInDB.model_validate(updated_org)


@router.get("/{org_id}/members", response_model=List[UserInDB])
async def get_organization_members(org_id: str, current_user: UserInDB = Depends(get_current_user)):
    """
    Get all members of a specific organization.
    """
    if not ObjectId.is_valid(org_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Organization ID")
        
    # Check if the authenticated user is part of the organization
    if current_user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this organization's members."
        )

    # Now, find all users who have this org_id
    members = await users_collection.find({"org_id": org_id}).to_list(length=100)
    
    return [UserInDB.model_validate(member) for member in members]