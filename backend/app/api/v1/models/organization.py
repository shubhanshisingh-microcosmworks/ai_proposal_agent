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

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2)
    industry: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    org_email: Optional[EmailStr] = None
    org_phone_number: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class OrganizationInDB(OrganizationBase):
    id: AnnotatedObjectId = Field(alias="_id")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

