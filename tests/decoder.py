#!/usr/bin/env python
# coding=utf-8

"""Human-readable JSON Decoder test cases for MongoEngine."""

import json
from unittest import TestCase

import mongoengine as db

from mongoengine_goodjson.decoder import generate_object_hook


class NoneFieldsTest(TestCase):
    """Test case if the model is not given."""

    def setUp(self):
        """Setup class."""
        self.hook = generate_object_hook(None)
        self.data = "{\"user\": \"56f63a716a8dec7705f36409\"}"
        self.expected_data = {"user": "56f63a716a8dec7705f36409"}

    def test_hook(self):
        """Given data should be decoded properly."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class ObjectIdDecodeTest(TestCase):
    """ObjectId Test."""

    def setUp(self):
        """Setup class."""
        from bson import ObjectId

        class TestModel(db.Document):
            user = db.ObjectIdField()

        self.model_cls = TestModel
        self.hook = generate_object_hook(self.model_cls)
        self.data = "{\"user\": \"56f63a716a8dec7705f36409\"}"
        self.expected_data = {"user": ObjectId("56f63a716a8dec7705f36409")}

    def test_hook(self):
        """Given data should be decoded properly."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class DBRefDecodeTest(TestCase):
    """DBRef Test."""

    def setUp(self):
        """Setup class."""
        import json
        from bson import DBRef, ObjectId

        class Source(db.Document):
            pass

        class Model(db.Document):
            src = db.ReferenceField(Source, dbref=True)

        self.src_cls = Source
        self.model_cls = Model
        self.src_id = ObjectId()
        self.data = json.dumps({
            "src": {"collection": "source", "id": str(self.src_id)}
        })
        self.expected_data = {"src": DBRef("source", self.src_id)}
        self.hook = generate_object_hook(self.model_cls)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)
