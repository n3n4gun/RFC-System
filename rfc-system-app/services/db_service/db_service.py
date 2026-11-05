from typing import Tuple

from loguru import logger

from core import (
    ApplicationOutcome,
    AuthentificationOutcome,
    RegistrationOutcome,
)
from infrastructure import ApplicationTable, Connection, UserTable
from models import CreateApplicationModel

connection = Connection()
user_table = UserTable()
application_table = ApplicationTable()

class DataBaseService:
    def registrate_new_user(self, user_reg_data: dict) -> RegistrationOutcome:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                transaction_status_outcome = user_table.insert_new_user(self._db_cursor, user_reg_data)

                if transaction_status_outcome == RegistrationOutcome.REGISTRATION_SUCCESS:
                    self._db_connection.commit()
                    logger.info('User registration committed')
                    return RegistrationOutcome.REGISTRATION_SUCCESS

                elif transaction_status_outcome == RegistrationOutcome.REGISTRATION_EMAIL_TAKEN:
                    return RegistrationOutcome.REGISTRATION_EMAIL_TAKEN

                elif transaction_status_outcome == RegistrationOutcome.REGISTRATION_DB_ERROR:
                    return RegistrationOutcome.REGISTRATION_DB_ERROR

            except Exception as unexpected_db_error:
                logger.error('Database operation failed error_type={}', type(unexpected_db_error).__name__)
                return RegistrationOutcome.REGISTRATION_DB_ERROR

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return RegistrationOutcome.REGISTRATION_DB_UNAVAILABLE

    def authentificate_user(self, user_login_data: dict) -> Tuple[AuthentificationOutcome, str | None]:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                transaction_status_outcome, user_id = user_table.get_user(self._db_cursor, user_login_data)

                if transaction_status_outcome != AuthentificationOutcome.LOGIN_SUCCESS:
                    return transaction_status_outcome, None

                is_active = user_table.check_user_is_active(self._db_cursor, user_id)

                if is_active is None:
                    return AuthentificationOutcome.LOGIN_DB_ERROR, None

                if is_active is False:
                    logger.warning('Authentication rejected: inactive user')
                    return AuthentificationOutcome.LOGIN_USER_INACTIVE, None

                logger.info('User authenticated')
                return AuthentificationOutcome.LOGIN_SUCCESS, user_id

            except Exception as error:
                logger.error(
                    'Authentication failed error_type={}',
                    type(error).__name__,
                )

                return AuthentificationOutcome.LOGIN_DB_ERROR, None

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return AuthentificationOutcome.LOGIN_DB_UNAVAILABLE, None

    def check_user_is_active(self, user_id: str) -> bool | None:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                is_active = user_table.check_user_is_active(self._db_cursor, user_id)

                return is_active

            except Exception as e:
                logger.error('Database operation failed error_type={}', type(e).__name__)

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return None

    def create_new_application(self, application_data: CreateApplicationModel) -> Tuple[ApplicationOutcome, None]:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                transaction_status_outcome = application_table.insert_new_application(self._db_cursor, application_data)

                if transaction_status_outcome == ApplicationOutcome.APPLICATION_SUCCESS:
                    self._db_connection.commit()
                    return ApplicationOutcome.APPLICATION_SUCCESS

                elif transaction_status_outcome == ApplicationOutcome.APPLICATION_DB_UNAVAILABLE:
                    return ApplicationOutcome.APPLICATION_DB_UNAVAILABLE

                elif transaction_status_outcome == ApplicationOutcome.APPLICATION_DB_ERROR:
                    return ApplicationOutcome.APPLICATION_DB_ERROR

            except Exception as unexpected_db_error:
                logger.error('Database operation failed error_type={}', type(unexpected_db_error).__name__)
                return RegistrationOutcome.REGISTRATION_DB_ERROR

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

