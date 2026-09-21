import os
import psycopg2

from loguru import logger
from psycopg2 import errors

from ports import ConnectionPort

class Connection(ConnectionPort):
    def db_connect(self) -> tuple | None:
        try:
            db_connection = psycopg2.connect(
                dbname = os.environ.get('DB_NAME'),
                user = os.environ.get('DB_USER'),
                password = os.environ.get('DB_PASSWORD'),
                host = os.environ.get('DB_HOST'),
                port = os.environ.get('DB_PORT')
            )
            db_cursor = db_connection.cursor()

            logger.success('DB SUCCESS: db connection has established')
            return db_connection, db_cursor

        except psycopg2.Error as db_connect_error:
            logger.error(f'DB ERROR: {db_connect_error}')
            return None, None

    def db_disconnect(self, db_connection, db_cursor):
        try:
            db_cursor.close()
            db_connection.close()

        except psycopg2.Error as db_disconnect_error:
            logger.error(f'DB ERROR: {db_disconnect_error}')
