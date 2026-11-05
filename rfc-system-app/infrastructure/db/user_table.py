import uuid
from datetime import datetime
from typing import Tuple

import psycopg2
from loguru import logger
from passlib.context import CryptContext

from core import (
    AuthentificationOutcome,
    get_password_hash,
    RegistrationOutcome,
    verify_password,
)
from ports import UserTableBasePort

class UserTable(UserTableBasePort):
    def insert_new_user(self, _db_cursor, user_reg_data: dict) -> RegistrationOutcome:
        new_user_id = str(uuid.uuid4().hex)
        user_reg_data = {'user_id' : new_user_id} | user_reg_data
        user_reg_data['password'] = get_password_hash(user_reg_data['password'])
        user_reg_data.update(
            {'registration_date': datetime.now().isoformat()}
        )

        try:
            users_table_columns = self.__get_users_table_columns()
            users_table_db_query = f'''
                INSERT INTO users_table ({(', '.join(users_table_columns))})
                VALUES ({', '.join(['%s'] * len(users_table_columns))})
            '''
            users_table_query_parameters = [user_reg_data[column] for column in users_table_columns]

            active_users_columns = self.__get_active_users_columns()
            active_users_db_query = f'''
                INSERT INTO active_users ({(', '.join(active_users_columns))})
                VALUES ({', '.join(['%s'] * len(active_users_columns))})
            '''

            active_users_query_parameters = [new_user_id, True]

            _db_cursor.execute(users_table_db_query, users_table_query_parameters)
            _db_cursor.execute(active_users_db_query, active_users_query_parameters)

            logger.debug('User insert executed; awaiting transaction commit')

            return RegistrationOutcome.REGISTRATION_SUCCESS

        except psycopg2.errors.UniqueViolation:
            logger.warning('Registration rejected: duplicate email')

            return RegistrationOutcome.REGISTRATION_EMAIL_TAKEN
        
        except psycopg2.Error as insert_new_user_error:
            logger.error('User insert failed sqlstate={}', insert_new_user_error.pgcode)

            return RegistrationOutcome.REGISTRATION_DB_ERROR

    def get_user(self, _db_cursor, user_login_data) -> Tuple[AuthentificationOutcome, str | None]:
        user_email = user_login_data['email']
        user_password = user_login_data['password']

        try:
            db_query = '''
                SELECT user_id, password
                FROM users_table
                WHERE email=%s
            '''
            query_parameters = (user_email,)
            _db_cursor.execute(db_query, query_parameters)

            user_row = _db_cursor.fetchone()

            if user_row:
                if verify_password(user_password, user_row[1]):
                    logger.info('User credentials verified')

                    return AuthentificationOutcome.LOGIN_SUCCESS, user_row[0]

                logger.warning('Authentication rejected: invalid credentials')

                return AuthentificationOutcome.LOGIN_AUTH_ERROR, None

            logger.warning('Authentication rejected: invalid credentials')
            return AuthentificationOutcome.LOGIN_AUTH_ERROR, None

        except psycopg2.Error as get_user_error:
            logger.error('User lookup failed sqlstate={}', get_user_error.pgcode)

            return AuthentificationOutcome.LOGIN_DB_ERROR, None

        except Exception as unexpected_db_error:
            logger.error('User lookup failed error_type={}', type(unexpected_db_error).__name__)

            return AuthentificationOutcome.LOGIN_DB_ERROR, None

    def delete_user(self, _db_cursor) -> bool:
        pass

    def check_user_is_active(self, _db_cursor, user_id: str) -> bool | None:
        try:
            db_query = f'''
                SELECT is_active
                FROM active_users
                WHERE user_id=%s
            '''
            _db_cursor.execute(db_query, (user_id,))
            row = _db_cursor.fetchone()

            if row is None:
                logger.warning('User activity record not found')
                return None

            return row[0]    # true || false

        except psycopg2.Error as check_user_is_active_error:
            logger.error('User activity lookup failed sqlstate={}', check_user_is_active_error.pgcode)

    def __get_users_table_columns(self) -> list:
        __columns = [
            'user_id', 'full_name',
            'email', 'department',
            'password', 'registration_date'
        ]

        return __columns

    def __get_active_users_columns(self) -> list:
        __columns = [
            'user_id', 'is_active'
        ]

        return __columns
