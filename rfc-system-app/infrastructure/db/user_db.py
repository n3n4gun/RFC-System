import os
import uuid
import psycopg2

from typing import Tuple
from datetime import datetime
from loguru import logger
from passlib.context import CryptContext

from ports import UserDataBasePort
from core import RegistrationOutcome, AuthentificationOutcome, get_password_hash, verify_password

class UserDataBase(UserDataBasePort):
    def insert_new_user(self, _db_cursor, user_reg_data: dict) -> RegistrationOutcome:
        new_user_id = str(uuid.uuid4().hex)
        user_reg_data = {'user_id' : new_user_id} | user_reg_data
        user_reg_data['password'] = get_password_hash(user_reg_data['password'])
        user_reg_data.update({'registration_date': datetime.now().isoformat()})

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

            logger.success('DB SUCCESS: user has inserted successfully')

            return RegistrationOutcome.REGISTRATION_SUCCESS

        except psycopg2.errors.UniqueViolation:
            logger.error(f"DB ERROR: user {user_reg_data['email']} has already existed")

            return RegistrationOutcome.REGISTRATION_EMAIL_TAKEN
        
        except psycopg2.Error as insert_new_user_error:
            logger.error(f'DB ERROR: {insert_new_user_error}')

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
                    logger.success(f"DB SUCCESS: user {user_email} has successfully authentificated")

                    return AuthentificationOutcome.LOGIN_SUCCESS, user_row[0]

                logger.error('DB ERROR: unsuccessful password hash verification')

                return AuthentificationOutcome.LOGIN_AUTH_ERROR, None

            return AuthentificationOutcome.LOGIN_AUTH_ERROR, None

        except psycopg2.Error as get_user_error:
            logger.error(f"DB ERROR: {get_user_error}")

            return AuthentificationOutcome.LOGIN_DB_ERROR, None

        except Exception as unexpected_db_error:
            logger.error(f"EXCEPTION: {unexpected_db_error}")

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
                logger.error(f'DB ERROR: no active_users record for user_id {user_id}')
                return None

            return row[0]    # true || false

        except psycopg2.Error as check_user_is_active_error:
            logger.error(f'DB ERROR: {check_user_is_active_error}')

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
