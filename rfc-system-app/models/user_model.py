from pydantic import BaseModel, EmailStr, SecretStr, Field

class User(BaseModel):
    user_id: str
    email: str

class LoginUserModel(BaseModel):
    email: EmailStr = Field(...)
    password: SecretStr = Field(..., min_length = 6, max_length = 15)

class RegisterUserModel(BaseModel):
    full_name: str = Field(..., min_length = 5, max_length = 50)
    email: EmailStr = Field(...)
    department: str = Field(..., min_length = 3, max_length = 25)
    password: SecretStr = Field(..., min_length = 6, max_length = 15)

class ActiveUserModel(BaseModel):
    user_id: str
    email: EmailStr
    is_active: bool = True
    