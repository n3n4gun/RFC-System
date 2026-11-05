import uuid

import psycopg2
from loguru import logger
from datetime import datetime

from ports import ApplicationTablePort
from models import CreateApplicationModel
from core import ApplicationOutcome

class ApplicationTable(ApplicationTablePort):
    def insert_new_application(self, _db_cursor, application_data: CreateApplicationModel) -> ApplicationOutcome:
        application_record = application_data.model_dump()
        application_id = str(uuid.uuid4().hex)
        application_record = {'application_id': application_id} | application_record
        application_record.update(
            {'created_at': datetime.now().isoformat()}
        )

        try:
            applications_table_columns = self.__get_applications_table_columns()
            applications_table_query = f'''
                INSERT INTO applications_table ({(', '.join(applications_table_columns))})
                VALUES ({', '.join(['%s'] * len(applications_table_columns))})
            '''
            applications_table_query_parameters = [application_record[column] for column in applications_table_columns]

            _db_cursor.execute(applications_table_query, applications_table_query_parameters)

            logger.debug('Application insert executed; awaiting transaction commit')

        except psycopg2.Error as error:
            logger.error('Application insert failed sqlstate={}', error.pgcode)
            raise

    def get_application(self, _db_cursor):
        pass

    def delete_application(self, _db_cursor):
        pass

    def __get_applications_table_columns(self) -> list:
        __columns = [
            'application_id', 'title',
            'service', 'priority',
            'description', 'created_at'
        ]

        return __columns
