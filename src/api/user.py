from fastapi import APIRouter, HTTPException, Request, status, Depends
from src.common.constants import Constants
from src.common.dependencies import get_user_table
from src.common.enums import UserType
from src.common.methods import custom_response, internal_server_error
from src.db.models import UserTable
from src.schemas.user import RegisterUser, UserProfile
from src.services.auth import bot_protection, response_with_extra_data, user_access, verify_jwt
from src.services.user import (
    create_new_user,
    get_user_data_by_user_id, 
    get_user_data_by_user_name,
    update_user_profile
)
from src.core.logging import logger

user_router = APIRouter()


@user_router.post("/register", status_code = status.HTTP_201_CREATED)
@bot_protection
async def read_item(request : Request, user_details : RegisterUser, users_table = Depends(get_user_table) ):
    try:
        user_data = get_user_data_by_user_name(user_details.user_name, users_table)
        if user_data:
            return custom_response(message = Constants.USERNAME_NOT_AVAILABLE,status_code = status.HTTP_400_BAD_REQUEST)
        
        new_user = UserTable(**user_details.model_dump())
        success = create_new_user(new_user, users_table)
        
        if not success:
            logger.info("Error: while creating new user in dynamoDB")
            return internal_server_error()

        return custom_response(
            message = "User is successfully registered",
            status_code = status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()

@user_router.put("/profile", status_code = status.HTTP_201_CREATED)
@user_access(allowed_user_type = UserType.DEVOTEE.value)
@verify_jwt
@bot_protection
async def update_profile(request : Request, user_profile_details : UserProfile, users_table = Depends(get_user_table)):
    try:
        user_data = get_user_data_by_user_id(user_profile_details.user_id, users_table)
        if not user_data:
            return custom_response(message = Constants.USER_NOT_FOUND, status_code = status.HTTP_400_BAD_REQUEST)
        
        success = update_user_profile(user_profile_details, users_table)
        if not success:
            return internal_server_error()
        
        extra_data = { "user": user_profile_details }
        return response_with_extra_data(Constants.USER_PROFILE_UPDATED,extra_data)
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()