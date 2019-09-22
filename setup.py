"""Distutils setup for awsscrubber"""
from setuptools import setup
from codecs import open

version = "0.0.1"

setup(
    name="awsscrubber",
    version=version,
    description="Python wrapper around the AWS Deidentifier",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="OS Independent",
    author="Robert Hafner",
    author_email="robert@radai.com",
    url="http://pypi.python.org/pypi/formatflowed",
    keywords=(),
    py_modules=["awsscrubber"],
    classifiers=[],
    install_requires=["boto3", "click", "black"],
    entry_points={"console_scripts": ["awsscrubber=awsscrubber:cli"]},
)
