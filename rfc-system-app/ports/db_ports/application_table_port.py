from abc import ABC, abstractmethod

class ApplicationTablePort(ABC):
    @abstractmethod
    def insert_new_application(self):
        raise NotImplemented

    @abstractmethod
    def get_application(self):
        raise NotImplemented

    @abstractmethod
    def delete_application(self):
        raise NotImplemented