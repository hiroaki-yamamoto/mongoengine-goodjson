#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ID replacement tests."""
from datetime import datetime, timedelta
import json
from unittest import TestCase, skip

from bson import ObjectId
from mongoengine import StringField

from mongoengine_goodjson.document import Document
from mongoengine_goodjson.fields import ObjectIDField


class NormalSchema(Document):
    """Normal document schama."""

    uid = ObjectIDField(primary_key=True)
    name = StringField(required=True)


class HasIDSchema(Document):
    """ID Duplicated schema."""

    uid = ObjectIDField(primary_key=True)
    id = ObjectIDField()
    name = StringField(required=True)


class IDReplaceTest(TestCase):
    """ID replace test."""

    def setUp(self):
        """Set up."""
        self.schema = NormalSchema
        self.model = self.schema(uid=ObjectId(), name="Test")
        self.exp = {"id": str(self.model.uid), "name": "Test"}

    def test_encode(self):
        """Encode Test."""
        dct = json.loads(self.model.to_json())
        self.assertEqual(dct, self.exp)

    @skip
    def test_decode(self):
        """Decode Test."""
        doc = NormalSchema.from_json(json.dumps(self.exp))
        self.assertEqual(doc.uid, self.model.uid)
        self.assertEqual(doc.to_mongo(), self.model.to_mongo())


class IDDuplicateTest(IDReplaceTest):
    """ID duplicated test case."""

    def setUp(self):
        """Set up."""
        self.schema = HasIDSchema
        self.model = self.schema(
            id=ObjectId.from_datetime(
                datetime.utcnow() - timedelta(hours=2),
            ),
            uid=ObjectId(), name="Test",
        )
        self.exp = {
            "id": str(self.model.id),
            "uid": str(self.model.uid),
            "name": "Test",
        }
