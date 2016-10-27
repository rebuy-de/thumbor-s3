# coding=utf-8
from distutils.core import setup

setup(
    name='thumbor-s3',
    version='0.2.0',
    author='Björn Häuser',
    author_email='b.haeuser@rebuy.com',
    packages=['thumbor_s3'],
    url='https://github.com/rebuy-de/thumbor-s3',
    license='LICENSE',
    description='Load images from private S3 buckets for thumbor',
    long_description=open('README.txt').read(),
    install_requires=[
        "tornado>=4.1.0,<5.0.0",
        "thumbor>=6.1.5,<7",
        ],
    extras_require={
        'tests': [
            "freezegun>=0.3.7,<1"
        ],
    },
    )
