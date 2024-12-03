from collections import defaultdict
from typing import Optional
from typing import Callable
from functools import wraps
from fastapi import Request, HTTPException, status
import jwt
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from src.common.constants import Constants
from src.common.enums import UserType
from src.common.methods import custom_response
from src.core.config import Config
from src.core.security import decode_jwt
import time
from botocore.exceptions import ClientError
from src.core.logging import logger


def create_access_token(data: dict, secret_key : str, algorithm : str, expires_minutes: Optional[int] = 30) -> str:
    """
    Create an access JWT token with the given data and expiration time in minutes.
    
    :param data: Data to be included in the JWT payload.
    :param expires_minutes: Time duration in minutes for token expiration.
    :return: Encoded JWT access token as a string.
    """
    to_encode = data.copy()

    # Set expiration time for the access token
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return f"Bearer {encoded_jwt}"

def create_refresh_token(data: dict, secret_key : str, algorithm : str,expires_minutes: Optional[int] = 60) -> str:
    """
    Create a refresh JWT token with the given data and expiration time in minutes.
    
    :param data: Data to be included in the JWT payload.
    :param expires_minutes: Time duration in minutes for token expiration.
    :return: Encoded JWT refresh token as a string.
    """
    to_encode = data.copy()

    # Set expiration time for the refresh token
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_google_token(google_user_token : str):
    try:
        response = id_token.verify_oauth2_token(
                    google_user_token, 
                    google_requests.Request(), 
                    Config.GOOGLE_CLIENT_ID
        )
        return response
    except ValueError as e:
        print(f"Error: {str(e)}")
        return None
    

def verify_jwt(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):        
        # Extract cookies from the request
        access_token = request.cookies.get("access_token")
        if not access_token or not access_token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid tokens."
            )

        # Extract token
        token = access_token.split(" ")[1]

        try:
            # Decode the token
            decoded_payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired."
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token."
            )

        # Extract additional parameters from request
        try:
            body = await request.json()  # Extract JSON body if it exists
        except Exception:
            body = {}

        user_id = body.get("user_id") or request.query_params.get("user_id") or decoded_payload.get("user_id")
        user_type = body.get("user_type") or request.query_params.get("user_type") or decoded_payload.get("user_type")

        if not user_id or not user_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required user information (user_id or user_type)."
            )
        
        # Check if the user_type from the request matches the decoded payload's user_type
        if user_id != decoded_payload.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch."
            )
            
        # Check if the user_type from the request matches the decoded payload's user_type
        if user_type != decoded_payload.get("user_type"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User type mismatch."
            )
        

        # Call the original function
        return await func(request, *args, **kwargs)

    return wrapper

def user_access(allowed_user_type: UserType):
    def decorator(func: Callable):
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Extract Authorization header from the request
            access_token = request.cookies.get("access_token")
            if not access_token or not access_token.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid tokens."
                )

            # Extract token
            token = access_token.split(" ")[1]

            try:
                # Decode the token
                decoded_payload = decode_jwt(token)
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired."
                )
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token."
                )

            # Check if the provided 'type' argument matches the payload's user_type
            if allowed_user_type != decoded_payload.get("user_type"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User type '{type}' does not have access to this resource."
                )

            # Call the original function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator

def add_record_with_ttl(record, ttl_seconds , table):
    try:
        creation_time = int(time.time())
        expiration_time = int(time.time()) + int(ttl_seconds)
        record["creation_time"] = creation_time
        record["expiration_time"] = expiration_time
        table.put_item(Item=record)
        return True
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return None
    
def update_record_with_ttl(update_data, ttl_seconds, table):
    try:
        # Calculate expiration and creation times
        expiration_time = int(time.time()) + ttl_seconds
        creation_time = int(time.time())
        
        # Construct the update expression
        update_expression = "SET expiration_time = :exp_time, creation_time = :crt_time, old_data = :old_data, new_data = :new_data, request_count = :request_count"
        expression_attribute_values = {
            ":exp_time": expiration_time,
            ":crt_time": creation_time,
            ":new_data" : update_data["new_data"],
            ":old_data" : update_data["old_data"],
            ":request_count" : update_data["request_count"],
        }
        # Update the item in the DynamoDB table
        response = table.update_item(
            Key={"id" : update_data["id"]},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )
        return True if response.get("ResponseMetadata").get("HTTPStatusCode") == 200 else None
        
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return None

def get_existing_data_by_id(id, temp_ttl_table):
    try:
        response = temp_ttl_table.get_item(
            Key={ "id": id }
        )
        return response["Item"] if response.get('Item') else None
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
def create_token(user_data,access_token = None, refresh_token = None, payload = None):
    response = defaultdict()
    if not payload:
        payload = { 
                    "user_id" : user_data["user_id"], 
                    "user_type" : user_data["user_type"]
                }
    if access_token:
        access_token = create_access_token(
                    data = payload,
                    secret_key = Config.APP_SECRET,
                    algorithm = Config.JWT_ALGO,
            )
        response["access_token"] = access_token
    if refresh_token:
        refresh_token = create_refresh_token(
                    data = payload,
                    secret_key = Config.APP_SECRET,
                    algorithm = Config.JWT_ALGO,
        )
        response["refresh_token"] = refresh_token

    return response

def process_user_login_with_token(user_data, extra_data):
    tokens = create_token(user_data, access_token=True, refresh_token=True)
    return response_with_extra_data(extra_data, tokens)
    
    
def response_with_extra_data(message, extra_data, tokens=None, status_code=status.HTTP_202_ACCEPTED):
    response = custom_response( message, status_code ,extra_keys={**extra_data} )
    if tokens:
        response.set_cookie( key="access_token", value=tokens["access_token"], httponly=True, secure=True, samesite="Strict" )
        response.set_cookie( key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=True, samesite="Strict" )
    return response


def bot_protection(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if Config.APP_ENV != "LOCAL":
            # Extract token from the header
            access_token = request.headers.get("Authorization")
            if not access_token:
                return custom_response(Constants.BOT_DETECTED, status.HTTP_403_FORBIDDEN)

            data = {
                "secret": Config.TURNSTILE_SECRET_KEY,
                "response": access_token
            }

            try:
                print(data)
                response = requests.post(Config.TURNSTILE_URL, data=data, timeout=10)
                response.raise_for_status()  # Raise error for HTTP status >= 400
                result = response.json()
                if not result.get("success"):
                    return custom_response(Constants.BOT_DETECTED, status.HTTP_403_FORBIDDEN)
            except Exception as e:
                logger.info(f"Error: {str(e)}")
                return custom_response(Constants.BOT_DETECTED, status.HTTP_403_FORBIDDEN)

        # Call the decorated function without `await` if synchronous
        return await func(request, *args, **kwargs)

    return wrapper