from abc import ABC, abstractmethod

class UserDataBasePort(ABC):
    @abstractmethod
    def insert_new_user(self):
        raise NotImplementedError

    @abstractmethod
    def get_user(self):
        raise NotImplementedError

    @abstractmethod
    def delete_user(self):
        raise NotImplementedError