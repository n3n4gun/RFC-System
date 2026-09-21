from pydantic import ValidationError

from models import LoginUserModel
from ports import UserLoginValidatorPort

class UserLoginValidator(UserLoginValidatorPort):
    def validate_user_login_data(self, user_login_data: dict) -> bool:
        try:
            LoginUserModel(**user_login_data)
            return True

        except ValidationError as validate_user_login_data_error:
            return False