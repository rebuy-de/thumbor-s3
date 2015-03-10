# coding=utf-8
from distutils.core import setup

setup(
    name='thumbor-s3',
    version='0.1.0',
    author='Björn Häuser',
    author_email='b.haeuser@rebuy.de',
    packages=['thumbor_s3'],
    url='https://github.com/rebuy-de/thumbor-s3',
    license='LICENSE',
    description='Load images from private S3 buckets for thumbor',
    long_description=open('README.txt').read(),
    install_requires=[
        "boto >= 2.36.0",
        "thumbor >= 4.11.1",
        ],
    )
