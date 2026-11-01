import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class JWTSettings(BaseSettings):
    SECRET_KEY: str = os.environ.get('SECRET_KEY')
    ALGORITHM: str = os.environ.get('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')

jwt_settings = JWTSettings()