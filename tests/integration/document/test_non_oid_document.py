#!/usr/bin/env python
# coding=utf-8

"""Non ObjectID tests."""

import json

from ..fixtures.email import Email
from ...con_base import DBConBase


class PrimaryKeyNotOidTest(DBConBase):
    """Good JSON encoder/decoder email as primary key test."""

    def setUp(self):
        """Set up the class."""
        self.email = Email.generate_test_data()
        self.data_id = self.email.to_dict()
        self.data_email = self.data_id.copy()

    def test_encode(self):
        """Email document should be encoded properly."""
        result = json.loads(self.email.to_json())
        self.assertEqual(self.data_id, result)

    def test_decode_id(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "id" field.
        """
        result = Email.from_json(json.dumps(self.data_id)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)

    def test_decode_email(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "email" field.
        """
        result = Email.from_json(json.dumps(self.data_email)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)
