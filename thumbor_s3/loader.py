from boto.exception import S3ResponseError
from boto.s3.connection import boto
from thumbor.utils import logger


def _normalize_url(context, url):
    bucket, url = url.split('/', 1)

    if bucket not in context.config.S3_LOADER_BUCKETS:
        return False

    config = context.config.S3_LOADER_BUCKETS[bucket]

    return bucket, config['base'] + url


def validate(context, url):
    return _normalize_url(context, url) is not False


def load(context, url, callback):
    bucket, url = _normalize_url(context, url)

    logger.debug("Retrieving image from bucket {0} with url {1}".format(bucket, url))

    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket, validate=False)
    key = bucket.get_key(url, validate=False)

    try:
        callback(key.get_contents_as_string())
    except S3ResponseError as e:
        logger.error("ERROR retrieving image from {0}".format(url), exc_info=e)
        callback(None)
