from pydantic import BaseModel, model_validator

from src.schemas.user import UserProfile


class GoogleUserToken(BaseModel):
    token: str
    

class Token(BaseModel):
    access_token: str
    @model_validator(mode="before")
    def validate_attributes(cls,values):
        values["access_token"] = f"Bearer {values['access_token']}"        
        return values
    
class LoginSucessResponse(BaseModel):
    tokens : Token
    user : UserProfile