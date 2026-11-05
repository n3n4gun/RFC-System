from enum import auto, Enum

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
    LOGIN_USER_INACTIVE = auto()

class ApplicationOutcome(Enum):
    APPLICATION_SUCCESS = auto()
    APPLICATION_DB_ERROR = auto()
    APPLICATION_DB_UNAVAILABLE = auto()
