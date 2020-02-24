#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Extended JSON Tests."""

import json
from unittest import TestCase

from bson import ObjectId
from mongoengine.fields import StringField
from mongoengine_goodjson.fields import ObjectIDField
from mongoengine_goodjson.document import Document


class NormalSchema(Document):
    """Normal document schama."""

    uid = ObjectIDField(primary_key=True)
    name = StringField(required=True)


class MongoDBExtendedJSONTest(TestCase):
    """MongoDB Extended Json Test."""

    def setUp(self):
        """Set up."""
        self.doc = NormalSchema(uid=ObjectId(), name="test")
        self.expected = {
            "_id": {"$oid": str(self.doc.uid)},
            "name": self.doc.name,
        }

    def test_generate(self):
        """Should Generate Extended JSON."""
        res = json.loads(self.doc.to_json(raw=True))
        self.assertEqual(res, self.expected)
