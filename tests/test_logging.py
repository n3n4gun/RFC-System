import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rfc-system-app'))

from loguru import logger

from logging_config import configure_logging, log_request


class RequestLoggingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        configure_logging()
        self.records = []
        self.sink = logger.add(lambda message: self.records.append(message.record))

    def tearDown(self):
        logger.remove(self.sink)

    async def test_concurrent_requests_have_separate_contexts(self):
        async def respond(request):
            await asyncio.sleep(0)
            logger.info('Inside request')
            return SimpleNamespace(status_code=201, headers={})

        request = SimpleNamespace(
            method='POST', scope={'route': SimpleNamespace(path='/application/new')}
        )
        responses = await asyncio.gather(
            log_request(request, respond), log_request(request, respond)
        )
        ids = {response.headers['X-Request-ID'] for response in responses}
        self.assertEqual(len(ids), 2)
        self.assertEqual(
            {record['extra']['request_id'] for record in self.records}, ids
        )
        logger.info('Outside request')
        self.assertEqual(self.records[-1]['extra']['request_id'], '-')

    async def test_http_error_level(self):
        async def respond(request):
            return SimpleNamespace(status_code=403, headers={})

        await log_request(SimpleNamespace(method='GET', scope={}), respond)
        self.assertEqual(self.records[-1]['level'].name, 'WARNING')

    async def test_exception_is_reraised_without_logging_secret(self):
        async def fail(request):
            raise RuntimeError('secret-password-and-token')

        with self.assertRaises(RuntimeError):
            await log_request(SimpleNamespace(method='POST', scope={}), fail)
        record = self.records[-1]
        self.assertEqual(record['level'].name, 'ERROR')
        self.assertIn('RuntimeError', record['message'])
        self.assertNotIn('secret-password-and-token', record['message'])
        self.assertIsNone(record['exception'])


if __name__ == '__main__':
    unittest.main()
