from typing import Tuple
from loguru import logger

from core import RegistrationOutcome, AuthentificationOutcome
from infrastructure import Connection, UserDataBase

connection = Connection()
user_data_base = UserDataBase()

class DataBaseService:
    def registrate_new_user(self, user_reg_data: dict) -> RegistrationOutcome:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                transaction_status_outcome = user_data_base.insert_new_user(self._db_cursor, user_reg_data)

                if transaction_status_outcome == RegistrationOutcome.REGISTRATION_SUCCESS:
                    self._db_connection.commit()
                    return RegistrationOutcome.REGISTRATION_SUCCESS

                elif transaction_status_outcome == RegistrationOutcome.REGISTRATION_EMAIL_TAKEN:
                    return RegistrationOutcome.REGISTRATION_EMAIL_TAKEN

                elif transaction_status_outcome == RegistrationOutcome.REGISTRATION_DB_ERROR:
                    return RegistrationOutcome.REGISTRATION_DB_ERROR

            except Exception as unexpected_db_error:
                logger.error(f'EXCEPTION: {unexpected_db_error}')
                return RegistrationOutcome.REGISTRATION_DB_ERROR

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return RegistrationOutcome.REGISTRATION_DB_UNAVAILABLE

    def authentificate_user(self, user_login_data: dict) -> Tuple[AuthentificationOutcome, str | None]:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                transaction_status_outcome, user_id = user_data_base.get_user(self._db_cursor, user_login_data)

                if transaction_status_outcome == AuthentificationOutcome.LOGIN_SUCCESS:
                    return AuthentificationOutcome.LOGIN_SUCCESS, user_id

                elif transaction_status_outcome == AuthentificationOutcome.LOGIN_AUTH_ERROR:
                    return AuthentificationOutcome.LOGIN_AUTH_ERROR, None

                elif transaction_status_outcome == AuthentificationOutcome.LOGIN_DB_ERROR:
                    return AuthentificationOutcome.LOGIN_DB_ERROR, None

            except Exception as e:
                logger.error(e)

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return AuthentificationOutcome.LOGIN_DB_UNAVAILABLE, None

    def check_user_is_active(self, user_id) -> bool | None:
        self._db_connection, self._db_cursor = connection.db_connect()

        if self._db_connection and self._db_cursor:
            try:
                is_active = user_data_base.check_user_is_active(self._db_cursor, user_id)

                if not is_active:
                    return None

                return is_active

            except Exception as e:
                logger.error(e)

            finally:
                connection.db_disconnect(self._db_connection, self._db_cursor)

        return None
