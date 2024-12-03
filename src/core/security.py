import bcrypt
from cachetools import TTLCache
from fastapi import HTTPException, status
import jwt
from src.core.config import Config
import secrets

jwt_cache = TTLCache(maxsize=100, ttl=5)

def hash_password(plain_password: str) -> str:
    # Generate a salt with bcrypt (this is a random value used in hashing)
    salt = bcrypt.gensalt()

    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)

    # Return the hashed password as a string
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def decode_jwt(token: str) -> dict:
    # Check if the token is already cached
    if token in jwt_cache:
        return jwt_cache[token]
    
    try:
        decoded_payload = jwt.decode(token, Config.APP_SECRET, algorithms=[Config.JWT_ALGO])
        # Cache the decoded payload for future requests for the next 5 seconds
        jwt_cache[token] = decoded_payload
        return decoded_payload
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


def generate_otp():
    """1 Generate a secure random 4-digit OTP and return it"""
    otp = f"{secrets.randbelow(10000):04}"  # Generate a 4-digit OTP
    return otp