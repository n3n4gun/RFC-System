from abc import ABC, abstractmethod

class UserRegValidatorPort(ABC):
    @abstractmethod
    def validate_user_reg_data(self):
        raise NotImplementedError

class UserLoginValidatorPort(ABC):
    @abstractmethod
    def validate_user_login_data(self):
        raise NotImplementedError