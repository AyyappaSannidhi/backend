from fastapi import Depends
import boto3
from src.core.config import Config

def get_db():
    return boto3.resource('dynamodb')

def get_user_table(db =  Depends(get_db)):
    return db.Table(Config.USERS_TABLE)

def get_temp_table(db =  Depends(get_db)):
    return db.Table(Config.TTL_TABLE)

def get_s3_client():
    return boto3.client('s3')