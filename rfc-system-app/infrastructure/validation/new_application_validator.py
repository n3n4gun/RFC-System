from pydantic import ValidationError

from models import CreateApplicationModel
from ports import NewApplicationValidatorPort

class NewApplicationValidator(NewApplicationValidatorPort):
    def validate_new_application(self, application_data: dict) -> CreateApplicationModel:
        return CreateApplicationModel(**application_data)