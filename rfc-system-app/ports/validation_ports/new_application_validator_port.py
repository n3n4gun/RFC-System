from abc import ABC, abstractmethod

class NewApplicationValidatorPort(ABC):
    @abstractmethod
    def validate_new_application(self):
        raise NotImplementedError