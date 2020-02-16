#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ObjectID test."""

import json
from unittest import TestCase

from bson import ObjectId
from mongoengine.document import Document
from mongoengine.errors import ValidationError
from mongoengine.fields import StringField
from mongoengine_goodjson.fields import ObjectIDField
from mongoengine_goodjson.document import Document as JSONDoc


class NormalSchema(Document):
    """Normal document schama."""

    uid = ObjectIDField()
    name = StringField(required=True)


class CustomSchema(JSONDoc):
    """Original document schema."""

    uid = ObjectIDField()
    name = StringField(required=True)


class NormalDocumentTest(TestCase):
    """Normal (or Standard) Document Test."""

    def setUp(self):
        """Set up."""
        self.doc = NormalSchema(
            uid=ObjectId(),
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {
            "uid": {"$oid": str(self.doc.uid)},
            "name": self.doc.name,
        }

    def test_serialization(self):
        """Should be serialized."""
        dct = json.loads(self.doc.to_json())
        self.assertEqual(dct, self.expected_dict)

    def test_deserializaton(self):
        """Should be deserialized."""
        doc = NormalSchema.from_json(json.dumps(self.expected_dict))
        # In pytohn checking equivalence between objects is impossible.
        # And therefore, it needs to convert into dict with to_mongo.
        self.assertEqual(doc.to_mongo(), self.doc.to_mongo())


class NormalSchemaCastingTest(NormalDocumentTest):
    """Normal Schema casting test."""

    def setUp(self):
        """Set up."""
        oid = str(ObjectId())
        self.doc = NormalSchema(
            uid=oid,
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {"uid": {"$oid": oid}, "name": self.doc.name}


class NormalSchemaInvalidCastingTest(TestCase):
    """Normal Schema casting test."""

    def setUp(self):
        """Set up."""
        oid = str("あばばばばばば")
        self.doc = NormalSchema(
            uid=oid,
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {"uid": {"$oid": oid}, "name": self.doc.name}

    def test_serialization(self):
        """Serialization should be failed."""
        with self.assertRaises(ValidationError) as e:
            self.doc.to_json()
        self.assertEqual(e.exception.field_name, "uid")


class CustomSchemaTest(NormalDocumentTest):
    """Custom schema document test."""

    def setUp(self):
        """Set up."""
        self.doc = CustomSchema(
            uid=ObjectId(),
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {
            "uid": str(self.doc.uid),
            "name": self.doc.name,
        }


class CustomSchemaCastingTest(CustomSchemaTest):
    """Custom Schema casting test."""

    def setUp(self):
        """Set up."""
        oid = str(ObjectId())
        self.doc = CustomSchema(
            uid=oid,
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {"uid": oid, "name": self.doc.name}


class CustomSchemaInvalidCastingTest(TestCase):
    """Custom Schema casting test."""

    def setUp(self):
        """Set up."""
        oid = str("あばばばばばば")
        self.doc = CustomSchema(
            uid=oid,
            name="Test",
        )
        # self.doc.save()
        self.expected_dict = {"uid": oid, "name": self.doc.name}

    def test_serialization(self):
        """Serialization should be failed."""
        with self.assertRaises(ValidationError) as e:
            self.doc.to_json()
        self.assertEqual(e.exception.field_name, "uid")
