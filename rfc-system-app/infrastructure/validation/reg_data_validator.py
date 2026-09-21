from pydantic import ValidationError

from ports import UserRegValidatorPort
from models import RegisterUserModel

class UserRegValidator(UserRegValidatorPort):
    def validate_user_reg_data(self, user_reg_data: dict) -> bool:
        try:
            RegisterUserModel(**user_reg_data)
            return True

        except ValidationError as validate_user_reg_data_error:
            return False