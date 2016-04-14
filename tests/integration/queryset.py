#!/usr/bin/env python
# coding=utf-8

"""Queryset integration tests."""

import json

from .schema import User
from .fixtures import users, users_dict
from ..connection_case import DBConBase


class UserSerializationDesrializationTest(DBConBase):
    """User serialization / deserialization integration test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None
        for user_el in users:
            user_el.save()

    def test_encode(self):
        """The data should be encoded properly."""
        result = json.loads(User.objects.to_json())
        self.assertListEqual(result, users_dict)

    def test_decode(self):
        """The data should be decoded properly."""
        result = User.objects.from_json(json.dumps(users_dict))
        self.assertListEqual(users, result)
