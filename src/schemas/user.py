import re
from typing import Optional
from fastapi import HTTPException,status
from pydantic import BaseModel, model_validator

from src.common.enums import UserAccountType, UserType

class RegisterUser(BaseModel):
    user_name : str
    password : str
    full_name : str
    email : Optional[str] = ""
    phone_number : Optional[str] = ""
    user_type : UserType
    account_type : UserAccountType = "internal"
    
    @model_validator(mode="before")
    def validate_attributes(cls,values):
        
        full_name = values["full_name"]
        if len(full_name) < 3 and re.search(r'[!@#$%^&*(),.?":{}|<>]', full_name):
            raise HTTPException(
                detail="Full Name should be less than 30 characters without special characters",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user_name = values["user_name"]
        if not len(user_name) >= 5 :
            raise HTTPException(
                detail="User Name must be atleast 5 characters long",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        phone_number = values.get("phone_number")
        if phone_number and phone_number.isdigit():
            if len(str(phone_number)) != 10:
                raise HTTPException(
                    detail="Phone Number must be 10 digits",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            raise HTTPException(
                detail="Invalid Phone Number",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        password = values["password"]
        if not len(password) >= 8 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(
                detail="Password must be atleast 8 characters long with atleast one special character",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        email = values.get("email")
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise HTTPException(
                detail="Invalid email address",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return values
    
class UserCredentials(BaseModel):
    user_name : str
    password : str
    user_type : UserType
    
    @model_validator(mode="before")
    def validate_attributes(cls,values):
        password = values["password"]
        if not len(password) >= 8 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(
                detail="Password must be atleast 8 characters long with atleast one special character",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return values
    

class UserProfile(BaseModel):
    user_id : str
    full_name : str
    user_name : str
    email : Optional[str] = ""
    phone_number : Optional[str] = ""
    picture : Optional[str] = ""
    user_type : UserType
    account_type : UserAccountType
    
    
    
    
class OtpUser(BaseModel):
    email : str
    
class OtpDetails(BaseModel):
    email : str
    otp : str
    
    @model_validator(mode="before")
    def validate_attributes(cls,values):
        email = values["email"]
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise HTTPException(
                detail="Invalid email address",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        otp = values["otp"]
        if not otp.isdigit() and not len(otp) == 4:
            raise HTTPException(
                detail="OTP must be 4 digits",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return values