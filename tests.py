import uuid
import unittest
import unittest.mock

from tornado import testing, web

from sprockets.mixins import correlation
from sprockets.mixins.correlation.mixins import correlation_id_logger


class RequestHandler(web.RequestHandler):

    def get(self, status_code):
        status_code = int(status_code)
        self.set_status(status_code)

        if status_code >= 300:
            raise web.HTTPError(status_code)
        self.write('status {0}'.format(status_code))


class CorrelatedRequestHandler(correlation.HandlerMixin, RequestHandler):
    pass


class CorrelationMixinTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return web.Application([
            (r'/status/(?P<status_code>\d+)', CorrelatedRequestHandler),
        ])

    def test_that_correlation_id_is_returned_when_successful(self):
        response = self.fetch('/status/200')
        self.assertIsNotNone(response.headers.get('Correlation-ID'))

    def test_that_correlation_id_is_returned_in_error(self):
        response = self.fetch('/status/500')
        self.assertIsNotNone(response.headers.get('Correlation-ID'))

    def test_that_correlation_id_is_copied_from_request(self):
        correlation_id = uuid.uuid4().hex
        response = self.fetch('/status/500',
                              headers={'Correlation-Id': correlation_id})
        self.assertEqual(response.headers['correlation-id'], correlation_id)


class CorrelationIDLoggerTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return web.Application([
            (r'/status/(?P<status_code>\d+)', CorrelatedRequestHandler),
            (r'/status/no-correlation/(?P<status_code>\d+)', RequestHandler),
        ], log_function=correlation_id_logger)

    def setUp(self):
        self.patcher = unittest.mock.patch(
            'sprockets.mixins.correlation.mixins.log.access_log')
        self.access_logger = self.patcher.start()
        super().setUp()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_lt_400_logs_info(self):
        for status in (200, 202):
            response = self.fetch('/status/{}'.format(status))

            self.access_logger.info.assert_any_call(
                "%d %s %.2fms {CID %s}",
                status,
                unittest.mock.ANY,
                unittest.mock.ANY,
                response.headers['correlation-id']
            )

    def test_gte_400_lt_500_logs_warning(self):
        for status in (400, 429):
            response = self.fetch('/status/{}'.format(status))

            self.access_logger.warning.assert_any_call(
                "%d %s %.2fms {CID %s}",
                status,
                unittest.mock.ANY,
                unittest.mock.ANY,
                response.headers['correlation-id']
            )

    def test_gte_500_logs_error(self):
        for status in (500, 504):
            response = self.fetch('/status/{}'.format(status))

            self.access_logger.error.assert_any_call(
                "%d %s %.2fms {CID %s}",
                status,
                unittest.mock.ANY,
                unittest.mock.ANY,
                response.headers['correlation-id']
            )

    def test_uses_correlation_id_from_header_if_missing_from_handler(self):
        correlation_id = uuid.uuid4().hex

        self.fetch('/status/no-correlation/200',
                   headers={'Correlation-Id': correlation_id})

        self.access_logger.info.assert_any_call(
            "%d %s %.2fms {CID %s}",
            200,
            unittest.mock.ANY,
            unittest.mock.ANY,
            correlation_id
        )

    def test_correlation_id_is_none_if_missing_from_handler_and_header(self):
        self.fetch('/status/no-correlation/200')

        self.access_logger.info.assert_any_call(
            "%d %s %.2fms {CID %s}",
            200,
            unittest.mock.ANY,
            unittest.mock.ANY,
            None
        )
