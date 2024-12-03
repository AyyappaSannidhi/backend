

from typing import Optional
import uuid
from pydantic import BaseModel, Field, model_validator

from src.common.enums import UserAccountType, UserType
from src.core.security import hash_password


class UserTable(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name : Optional[str] = ""
    user_name : str
    password : Optional[str] = ""
    email : Optional[str] = ""
    phone_number : Optional[str] = ""
    picture : Optional[str] = ""
    user_type : UserType
    account_type : UserAccountType
    
    @model_validator(mode="before")
    def hash_password(cls,values):
        if values.get("password"):
            values["password"] = hash_password(values["password"])
        return values
    
    