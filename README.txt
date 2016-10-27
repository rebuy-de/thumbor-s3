=======================================
Thumbor S3 File Loader
=======================================

Uses boto to retrieve images from S3 to use with `thumbor <https://github.com/thumbor/thumbor>`_.

Only useful if the S3 assets are not public available.

Config looks like this:
```
S3_LOADER_BUCKETS = {
  '<bucketname>': {
    'base': '/',
    'region': 'eu-west-1'
  }
}
```
