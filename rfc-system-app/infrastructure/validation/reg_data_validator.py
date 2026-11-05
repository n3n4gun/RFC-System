from loguru import logger
from pydantic import ValidationError

from models import RegisterUserModel
from ports import UserRegValidatorPort

class UserRegValidator(UserRegValidatorPort):
    def validate_user_reg_data(self, user_reg_data: dict) -> bool:
        try:
            RegisterUserModel(**user_reg_data)
            return True

        except ValidationError as validate_user_reg_data_error:
            logger.warning('Registration data validation failed')
            return False