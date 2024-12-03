from dataclasses import dataclass
import os

from dotenv import load_dotenv
load_dotenv()

@dataclass(slots=True)
class Config():
    APP_ENV          = os.environ.get('APP_ENV')
    APP_SECRET       = os.environ.get('APP_SECRET')
    JWT_ALGO         = os.environ.get('JWT_ALGO')
    JWT_EXPIRY_MIN   = int(os.environ.get('JWT_EXPIRY_MIN'))
    AWS_S3_BUCKET_NAME   = os.environ.get('AWS_S3_BUCKET_NAME')
    ALLOWED_ORIGINS  = os.environ.get('ALLOWED_ORIGINS')
    GOOGLE_CLIENT_ID  = os.environ.get('GOOGLE_CLIENT_ID')
    MAIL_APP_PASSWORD = os.environ.get('MAIL_APP_PASSWORD')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
    TURNSTILE_URL = os.environ.get('TURNSTILE_URL')
    USERS_TABLE = os.environ.get('USERS_TABLE')
    TTL_TABLE = os.environ.get('TTL_TABLE')
    BOT_PROTECTION=os.environ.get('BOT_PROTECTION')

