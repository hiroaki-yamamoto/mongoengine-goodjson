#!/usr/bin/env python
# coding=utf-8

"""Database Connection TestCase base class."""

from unittest import TestCase
import mongoengine as db


class DBConBase(TestCase):
    """Database Connection TestCase base class."""

    @classmethod
    def setUpClass(cls):
        """Set up database connection."""
        cls.db = db.connect("goodjson_test", host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        """Teardown database connection."""
        cls.db.drop_database("goodjson_test")
