#!/usr/bin/env python
# coding=utf-8
"""Setup script."""

import sys
from setuptools import setup, find_packages

dependencies = ["mongoengine", "dateutils"]
desc = "More human readable JSON serializer/de-serializer for MongoEngine"
version = "0.11.3"
if sys.version_info < (2, 7):
    raise RuntimeError("Not supported on earlier then python 2.7.")

try:
    from functools import singledispatch
except ImportError:
    dependencies.append("singledispatch")

try:
    with open('README.rst') as readme:
        long_desc = readme.read()
except Exception:
    long_desc = None

setup(
    name="mongoengine_goodjson",
    version=version,
    description=desc,
    long_description=long_desc,
    packages=find_packages(exclude=["tests"]),
    install_requires=dependencies,
    zip_safe=False,
    author="Hiroaki Yamamoto",
    author_email="hiroaki@hysoftware.net",
    license="MIT",
    keywords="json mongoengine mongodb",
    url="https://github.com/hiroaki-yamamoto/mongoengine-goodjson",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
    ]
)
