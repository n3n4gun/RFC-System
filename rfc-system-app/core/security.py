import os

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from .config import jwt_settings

pwd_context = CryptContext(
    schemes = os.environ.get('SCHEMES'),
    deprecated = os.environ.get('DEPRECATED')
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(plain_password: str):
    return pwd_context.hash(plain_password)

def create_access_token(user_payload: dict) -> str:
    user_payload_to_encode = user_payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_payload_to_encode.update({'exp': expire})
    user_jwt_token = jwt.encode(
        user_payload_to_encode,
        jwt_settings.SECRET_KEY,
        algorithm = jwt_settings.ALGORITHM
    )

    return user_jwt_token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            jwt_settings.SECRET_KEY,
            algorithms = [jwt_settings.ALGORITHM]
        )

        return payload

    except JWTError:
        return None