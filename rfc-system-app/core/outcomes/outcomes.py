from enum import Enum, auto

class RegistrationOutcome(Enum):
    REGISTRATION_SUCCESS = auto()
    REGISTRATION_EMAIL_TAKEN = auto()
    REGISTRATION_DB_ERROR = auto()
    REGISTRATION_DB_UNAVAILABLE = auto()

class AuthentificationOutcome(Enum):
    LOGIN_SUCCESS = auto()
    LOGIN_AUTH_ERROR = auto()
    LOGIN_DB_ERROR = auto()
    LOGIN_DB_UNAVAILABLE = auto()
