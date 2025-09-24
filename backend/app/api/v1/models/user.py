from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from pydantic_core import core_schema
from typing_extensions import Annotated
from bson import ObjectId

# This PyObjectId is not strictly necessary but is a good example of Pydantic v2's advanced validation.
# We will continue to use the alias method for simplicity as it works perfectly.
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ])
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, _handler: Any) -> dict[str, Any]:
        return {"type": "string", "pattern": "^[a-fA-F0-9]{24}$"}

# Corrected type for the ID, ensuring it is a string for API responses
# while handling both ObjectId and string input.
AnnotatedObjectId = Annotated[str, BeforeValidator(str)]

# Model for changing password
class PasswordChange(BaseModel):
    new_password: str = Field(..., min_length=8)

# Models for the nested arrays
class Education(BaseModel):
    school_name: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: Optional[str] = None

class Experience(BaseModel):
    company_name: str
    job_title: str
    start_date: str
    end_date: Optional[str] = None
    is_current: Optional[bool] = False

class Project(BaseModel):
    project_title: str
    description: Optional[str] = None

# 🐛 FIXED: The Profile model is a single object, not a list.
class Profile(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class Skill(BaseModel):
    skill_name: str
    endorsements: Optional[int] = 0
    proficiency: Optional[str] = None

# Main User Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# The comprehensive model for updating user information
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    # 🐛 FIXED: Profile is a single object, not a list.
    role: Optional[str] = "freelancer"
    profile: Optional[Profile] = None 
    education: Optional[List[Education]] = None
    experience: Optional[List[Experience]] = None
    projects: Optional[List[Project]] = None
    skills: Optional[List[Skill]] = None
    is_deleted: Optional[bool] = False
    org_id: Optional[str] = None

class UserInDB(UserBase):
    id: AnnotatedObjectId = Field(alias="_id")
    password_hash: str
    role: Optional[str] = "freelancer"
    is_active: Optional[bool] = True
    org_id: Optional[str] = None
    
    # 🐛 FIXED: Profile is a single dict, not a list of dicts.
    profile: Optional[dict] = None
    education: Optional[List[dict]] = None
    experience: Optional[List[dict]] = None
    projects: Optional[List[dict]] = None
    skills: Optional[List[dict]] = None
    is_deleted: Optional[bool] = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}