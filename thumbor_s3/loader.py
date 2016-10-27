import hashlib
import hmac
import os
from datetime import datetime
from functools import partial

import tornado.httpclient
from thumbor.loaders.http_loader import return_contents
from thumbor.utils import logger
from tornado.concurrent import return_future

method = 'GET'
service = 's3'
host_template = 's3-{}.amazonaws.com'
endpoint_template = 'https://s3-{}.amazonaws.com'

empty_payload_hash = hashlib.sha256('').hexdigest()
signed_headers = 'host;x-amz-content-sha256;x-amz-date'
algorithm = 'AWS4-HMAC-SHA256'


def _normalize_url(context, url):
    bucket, url = url.split('/', 1)

    if bucket not in context.config.S3_LOADER_BUCKETS:
        return False

    config = context.config.S3_LOADER_BUCKETS[bucket]

    return '/' + bucket + config['base'] + url, config['region']


def validate(context, url):
    if '/' not in url:
        return False

    return _normalize_url(context, url) is not False


def get_signature(url, region):
    t = datetime.utcnow()
    x_amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date = t.strftime('%Y%m%d')

    host = get_host(region)

    headers = '\n'.join(
        ['host:' + host, 'x-amz-content-sha256:' + empty_payload_hash, 'x-amz-date:' + x_amz_date, ""]
    )

    signature_request = '\n'.join(
        ['GET', url, '', headers, signed_headers, empty_payload_hash]
    )

    credentials = '/'.join([date, region, service, 'aws4_request'])
    signature_parts = '\n'.join([
        algorithm,
        x_amz_date,
        credentials,
        hashlib.sha256(signature_request).hexdigest()
    ])

    signing_key = get_signing_key(__get_secret_key(), date, region, service)
    signature_parts = hmac.new(signing_key, signature_parts.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = '{0} Credential={1}/{2}, SignedHeaders={3},Signature={4}'.format(
        algorithm, __get_access_key(), credentials, signed_headers, signature_parts
    )

    return authorization_header, empty_payload_hash, x_amz_date


@return_future
def load(context, url, callback):
    url, region = _normalize_url(context, url)

    logger.debug("Retrieving image with url {0}".format(url))

    authorization_header, payload_hash, date = get_signature(url, region)

    client = tornado.httpclient.AsyncHTTPClient()

    req = tornado.httpclient.HTTPRequest(
        url=endpoint_template.format(region) + url,
        follow_redirects=False,
        headers={
            'Authorization': authorization_header,
            'x-amz-content-sha256': empty_payload_hash,
            'x-amz-date': date
        }
    )

    start = datetime.now()
    client.fetch(req, callback=partial(return_contents, url=url, callback=callback, context=context, req_start=start))


def get_host(region):
    return host_template.format(region)


def get_signing_key(key, date, region, service):
    signed_date = sign(('AWS4' + key).encode('utf-8'), date)
    signed_region = sign(signed_date, region)
    signed_service = sign(signed_region, service)

    return sign(signed_service, 'aws4_request')


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def __get_access_key():
    return os.environ.get('AWS_ACCESS_KEY_ID')


def __get_secret_key():
    return os.environ.get('AWS_SECRET_ACCESS_KEY')
