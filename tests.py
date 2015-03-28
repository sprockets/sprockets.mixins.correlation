import uuid
import unittest

from tornado import testing, web

from sprockets.mixins import correlation


class CorrelatedRequestHandler(correlation.HandlerMixin, web.RequestHandler):

    def get(self, status_code):
        status_code = int(status_code)
        if status_code >= 300:
            raise web.HTTPError(status_code)
        self.write('status {0}'.format(status_code))


class CorrelationMixinTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        return web.Application([
            (r'/status/(?P<status_code>\d+)', CorrelatedRequestHandler),
        ])

    def test_that_correlation_id_is_returned_when_successful(self):
        self.http_client.fetch(self.get_url('/status/200'), self.stop)
        response = self.wait()
        self.assertIsNotNone(response.headers.get('Correlation-ID'))

    def test_that_correlation_id_is_returned_in_error(self):
        self.http_client.fetch(self.get_url('/status/500'), self.stop)
        response = self.wait()
        self.assertIsNotNone(response.headers.get('Correlation-ID'))

    def test_that_correlation_id_is_copied_from_request(self):
        correlation_id = uuid.uuid4().hex
        self.http_client.fetch(self.get_url('/status/200'), self.stop,
                               headers={'Correlation-Id': correlation_id})
        response = self.wait()
        self.assertEqual(response.headers['correlation-id'], correlation_id)
