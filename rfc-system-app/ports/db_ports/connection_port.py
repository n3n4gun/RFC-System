from abc import ABC, abstractmethod

class ConnectionPort(ABC):
    @abstractmethod
    def db_connect(self):
        raise NotImplementedError

    @abstractmethod
    def db_disconnect(self):
        raise NotImplementedError