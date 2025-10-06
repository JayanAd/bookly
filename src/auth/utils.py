from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
from src.config import Config
import logging

passwd_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY = 3600

def generate_password_hash(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return passwd_context.verify(plain_password, hashed_password)

def create_access_token(user_data:dict, expiry:timedelta = None, refresh:bool = False ):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    
    token = jwt.encode(
        payload = payload,
        key = Config.JWT_SECRET,
        algorithm = Config.JWT_ALGORITHM,
    )
    
    return token

def decode_token(token:str)-> dict:
    try:
        payload = jwt.decode(
            jwt= token,
            key= Config.JWT_SECRET,
            algorithms= [Config.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError as e:
        logging.exception("Token decoding failed", exc_info=e)
        return None
        