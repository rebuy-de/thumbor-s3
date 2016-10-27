import os
from unittest import TestCase

from derpconf.config import Config
from freezegun import freeze_time
from pyvows.core import expect
from thumbor.context import Context
from thumbor.loaders import LoaderResult
from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from thumbor_s3.loader import _normalize_url
from thumbor_s3.loader import get_signature
from thumbor_s3.loader import load
from thumbor_s3.loader import validate


class MainHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.write('Hello')


def get_config():
    config = Config.load(None)
    config.define("S3_LOADER_BUCKETS", {'bucket-name': {'base': '/', 'region': 'eu-west-1'}}, 'loader buckets')
    return config


class ConfigValidationTestCase(TestCase):
    def test_should_normalize_url(self):
        call_context = Context()
        config = get_config()
        call_context.config = config

        url, region = _normalize_url(call_context, 'bucket-name/path/to/file.jpg')

        self.assertEqual("eu-west-1", region)
        self.assertEqual("/bucket-name/path/to/file.jpg", url)

    def test_should_not_validate_for_invalid_bucket(self):
        call_context = Context()
        config = get_config()
        call_context.config = config

        self.assertFalse(validate(call_context, 'non-existing/path/to/file.jpg'))


@freeze_time('2016-10-07 00:00:00')
class SignatureCalculationTestCase(TestCase):
    def setUp(self):
        os.environ["AWS_ACCESS_KEY_ID"] = 'access-key'
        os.environ["AWS_SECRET_ACCESS_KEY"] = 'secret-key'

    def test_should_calculate_correct_signature(self):
        authorization_header, _, _ = get_signature("foo", "bar")

        self.assertEqual(
            'AWS4-HMAC-SHA256 Credential=access-key/20161007/bar/s3/aws4_request, SignedHeaders=' +
            'host;x-amz-content-sha256;x-amz-date,Signature=' +
            'f63c2de0492e33849162e9646f026c0261045a75dd1232ca877e0b53776f8cd8',
            authorization_header)


class HttpLoaderTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(HttpLoaderTestCase, self).setUp()

        os.environ["AWS_ACCESS_KEY_ID"] = 'access-key'
        os.environ["AWS_SECRET_ACCESS_KEY"] = 'secret-key'

    def get_app(self):
        application = Application([
            (r"/.*", MainHandler),
        ])

        return application

    def test_load_with_callback(self):
        import thumbor_s3
        thumbor_s3.loader.endpoint_template = self.get_url('')

        url = 'bucket-name/path/to/file.jpg'
        config = get_config()
        ctx = Context(None, config, None)

        load(ctx, url, self.stop)
        result = self.wait()
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal('Hello')
        expect(result.successful).to_be_true()

    def test_should_return_a_future(self):
        url = 'bucket-name/path/to/file.jpg'

        config = get_config()
        ctx = Context(None, config, None)

        future = load(ctx, url, self.stop)
        expect(isinstance(future, Future)).to_be_true()
