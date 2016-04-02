#!/usr/bin/env python
# coding=utf-8
"""Setup script."""

import sys
from setuptools import setup, find_packages

dependencies = ["mongoengine", "dateutils"]

if sys.version_info < (2, 7):
    raise RuntimeError("Not supported on earlier then python 2.7.")

try:
    from functools import singledispatch
except ImportError:
    dependencies.append("singledispatch")

setup(
    name="mongoengine_goodjson",
    version="0.0.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=dependencies,
    zip_safe=False,
    author="Hiroaki Yamamoto",
    author_email="hiroaki@hysoftware.net",
    description="JSON serializer/de-serializer for humans and MongoEngine",
    license="MIT",
    keywords="json mongoengine mongodb",
    url="https://github.com/hiroaki-yamamoto/mongoengine-goodjson",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
    ]
)
