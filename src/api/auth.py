import time
from fastapi import (
    APIRouter,
    Request, 
    status, 
    Depends
)
from src.common.constants import Constants
from src.common.dependencies import get_temp_table, get_user_table
from src.common.enums import UserAccountType, UserType
from src.common.methods import custom_response, internal_server_error
from src.common.templates import get_otp_template
from src.core.security import generate_otp
from src.db.models import UserTable
from src.schemas.auth import GoogleUserToken
from src.schemas.user import OtpDetails, OtpUser, UserCredentials
from src.services.auth import (
    add_record_with_ttl,
    bot_protection,
    create_token,
    get_existing_data_by_id,
    response_with_extra_data,
    update_record_with_ttl,
    verify_google_token
)
from src.services.email import send_email
from src.services.user import (
    create_new_user,
    get_user_data_by_user_id,
    get_user_data_by_user_name,
    verify_user
)
from src.core.logging import logger

auth_router = APIRouter()

@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
@bot_protection
async def login(request : Request, user_credentials : UserCredentials, users_table = Depends(get_user_table) ):
    try:
        user_data = get_user_data_by_user_name(user_credentials.user_name, users_table)
        print(user_data)
        if not user_data:
            return custom_response(Constants.REGISTER_FIRST, status.HTTP_400_BAD_REQUEST)
            
        success = verify_user(user_credentials, user_data)
        if not success:
            return custom_response(Constants.INVALID_USERNAME_AND_PASSWORD, status.HTTP_400_BAD_REQUEST)

        user_profile = {
                "user_id" : user_data["user_id"],
                "full_name" : user_data["full_name"],
                "user_name" : user_data["user_name"],
                "email" : user_data["email"],
                "phone_number" : user_data["phone_number"],
                "picture" : user_data["picture"],
                "user_type" : user_data["user_type"],
                "account_type" : user_data["account_type"]
        }
        
        extra_data = { "user": user_profile }
        tokens = create_token(user_data, access_token=True, refresh_token=True)
        return response_with_extra_data(Constants.LOGIN_SUCCESS, extra_data, tokens)

    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()
        
@auth_router.post("/google_login", status_code=status.HTTP_202_ACCEPTED)
async def google_login(request : Request, token : GoogleUserToken, users_table = Depends(get_user_table)):
    try : 
        google_user_data = verify_google_token(token.token)
        if not google_user_data:
            return custom_response(Constants.INVALID_TOKEN, status.HTTP_401_UNAUTHORIZED)
        
        if not google_user_data["email_verified"] and not google_user_data["sub"]:
            return custom_response(Constants.NOT_GOOGLE_VERIFIED_USER, status.HTTP_401_UNAUTHORIZED)
        
        user_data = get_user_data_by_user_id(google_user_data["sub"], users_table)
        if not user_data:
            success = create_new_user(
                new_user = UserTable(
                    user_id = google_user_data["sub"],
                    full_name = google_user_data["name"],
                    user_name = google_user_data["email"],
                    password = "",
                    email = google_user_data["email"],
                    phone_number = "",
                    picture = google_user_data["picture"],
                    user_type = UserType.DEVOTEE.value,
                    account_type = UserAccountType.GOOGLE.value
                ), 
                users_table=users_table
            )
            if not success:
                return internal_server_error()
            
        token_payload = { 
            "user_id" : google_user_data["sub"], 
            "user_type" : UserType.DEVOTEE.value
        }
        
        profile_details = {
            "user_id" : google_user_data["sub"],
            "full_name" : google_user_data["name"],
            "user_name" : google_user_data["email"],
            "email" : google_user_data["email"],
            "phone_number" : "",
            "picture" : google_user_data["picture"],
            "user_type" : UserType.DEVOTEE.value,
            "account_type" : UserAccountType.GOOGLE.value
        }
    
        extra_data = { "user": profile_details }
        tokens = create_token(user_data, access_token=True, refresh_token=True,payload=token_payload)
        return response_with_extra_data(Constants.LOGIN_SUCCESS,extra_data, tokens)

    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()
    
@auth_router.post("/otp_request", status_code=status.HTTP_201_CREATED)
@bot_protection
async def otp_login(request : Request, user_details: OtpUser, temp_ttl_table=Depends(get_temp_table)):
    try:
        existing_otp_record = get_existing_data_by_id(user_details.email, temp_ttl_table)
        otp = str(generate_otp())
        
        # Check for too many OTP requests
        if existing_otp_record and int(existing_otp_record["request_count"]) > 3:
            return custom_response(Constants.MANY_OTP_REQUESTS, status.HTTP_400_BAD_REQUEST)
        
        # Prepare record for updating or adding
        record = {
            "id": user_details.email,
            "new_data": otp,
            "request_count": existing_otp_record["request_count"] + 1 if existing_otp_record else 1,
        }
        if existing_otp_record:
            record["old_data"] = existing_otp_record["new_data"]

        # Save record with TTL
        success = update_record_with_ttl(record, ttl_seconds=600, table=temp_ttl_table) if existing_otp_record \
            else add_record_with_ttl(record, ttl_seconds=600, table=temp_ttl_table)

        if not success:
            return internal_server_error()

        # Send OTP email
        email_body = get_otp_template(user_details.email, otp)
        if not send_email(user_details.email, Constants.OTP_SUBJECT, email_body):
            return internal_server_error()

        return custom_response(Constants.EMAIL_SENT, status.HTTP_201_CREATED)

    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()

@auth_router.post('/otp_verify')
@bot_protection
async def otp_verify(request : Request, otp_details: OtpDetails, temp_ttl_table = Depends(get_temp_table), users_table = Depends(get_user_table)):
    try:
        existing_otp_record = get_existing_data_by_id(otp_details.email, temp_ttl_table)
        if not existing_otp_record:
            return custom_response(Constants.PLEASE_REQUEST_FIRST, status.HTTP_400_BAD_REQUEST)
        
        if existing_otp_record["expiration_time"] < int(time.time()):
            return custom_response(Constants.OTP_EXPIRED_OR_INVALID, status.HTTP_400_BAD_REQUEST)

        if existing_otp_record["new_data"] != otp_details.otp and existing_otp_record.get("old_data") != otp_details.otp:
            return custom_response(Constants.OTP_EXPIRED_OR_INVALID, status.HTTP_400_BAD_REQUEST)
        
        existing_user = get_user_data_by_user_name(otp_details.email, users_table)
        if existing_user:
            del existing_user["password"]
            extra_data = { "user": existing_user }
            print(existing_user,"sldfjdslf")
            tokens = create_token(existing_user, access_token=True, refresh_token=True)
            return response_with_extra_data(Constants.LOGIN_SUCCESS,extra_data, tokens,status.HTTP_202_ACCEPTED)
        new_user = UserTable(
            user_name = otp_details.email,
            email = otp_details.email,
            user_type = UserType.DEVOTEE.value,
            account_type = UserAccountType.OTP.value
        )
        success = create_new_user(new_user, users_table)
        if not success:
            return internal_server_error()
        extra_data = { "user": new_user.model_dump(exclude={"password"}) }
        print(extra_data)
        tokens = create_token(new_user, access_token=True, refresh_token=True)
        return response_with_extra_data( Constants.LOGIN_SUCCESS, extra_data, tokens, status.HTTP_202_ACCEPTED )
    
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return internal_server_error()
