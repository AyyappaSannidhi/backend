from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from src.common.methods import internal_server_error
from src.core.security import verify_password
from src.schemas.user import UserCredentials, UserProfile
from src.db.models import UserTable
from src.core.logging import logger

def get_user_data_by_user_id(user_id, users_table):
    try:
        response = users_table.get_item(
            Key={ "user_id": user_id }
        )
        return response["Item"] if response.get('Item') else None
    except Exception as e:
        logger.info(f"Error: {str(e)}, getting data from dynamoDB")
        internal_server_error()
    
def get_user_data_by_user_name(user_name, users_table):
    try:
        response  = users_table.scan(FilterExpression=Attr('user_name').eq(user_name))
        return response["Items"][0] if response.get('Items') else None
    except Exception as e:
        logger.info(f"Error: {str(e)}, getting data from dynamoDB")
        internal_server_error()

def update_user_profile(user_details : UserProfile, users_table):
    try:
        response = users_table.update_item(
            Key = { "user_id" : user_details.user_id },
            UpdateExpression = "SET full_name = :full_name, email = :email, phone_number = :phone_number, picture = :picture",
            ExpressionAttributeValues = {
                ":full_name" : user_details.full_name,
                ":email" : user_details.email,
                ":phone_number" : user_details.phone_number,
                ":picture" : user_details.picture
            }
        )
        return True if response.get("ResponseMetadata").get("HTTPStatusCode") == 200 else None
    except ClientError as e:
        logger.info(f"Error: {str(e)}, while updating user in dynamoDB")
        return None
    
def create_new_user(new_user : UserTable, users_table):
    try:
        response = users_table.put_item(
            Item = {
                        "user_id" : new_user.user_id,
                        "full_name" : new_user.full_name or "",
                        "user_name" : new_user.user_name or "",
                        "password" : new_user.password or "",
                        "email" : new_user.email or "",
                        "phone_number" : new_user.phone_number or "",
                        "picture" : new_user.picture or "",
                        "user_type" : new_user.user_type.value or "",
                        "account_type" : new_user.account_type.value or ""
                    }
        )
        return True if response.get("ResponseMetadata").get("HTTPStatusCode") == 200 else None
    except ClientError as e:
        logger.info(f"Error: {str(e)}, while creating new user in dynamoDB")
        return None
    
    
def verify_user(user_credentials : UserCredentials, user_data):
    try:
        if user_credentials.user_type.value != user_data["user_type"] or not verify_password(user_credentials.password, user_data["password"]):
            return None
        return True
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return None
    

def create_profile(user_details : UserTable):
    return {
            "user_id" : user_details.user_id,
            "full_name" : user_details.full_name,
            "user_name" : user_details.email,
            "email" : user_details.email,
            "phone_number" : user_details.phone_number,
            "picture" : user_details.picture,
            "user_type" : user_details.user_type.value,
            "account_type" : user_details.account_type.value
        }
    