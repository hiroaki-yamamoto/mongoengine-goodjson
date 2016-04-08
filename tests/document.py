#!/usr/bin/env python
# coding=utf-8

"""New Document serializer/deserializer."""

from unittest import TestCase

from bson import ObjectId
import mongoengine as db
from mongoengine_goodjson import GoodJSONEncoder, Document, EmbeddedDocument

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class ToJSONTest(TestCase):
    """Good JSON Encoder invocation test."""

    def setUp(self):
        """Setup the class."""
        class TestDocument(Document):
            title = db.StringField()

        class TestEmbeddedDocument(EmbeddedDocument):
            title = db.StringField()

        class TestFollowReference(Document):
            reference = db.ReferenceField("self")

        self.reference_model = TestFollowReference()

        self.model_cls = TestDocument
        self.model = TestDocument(title="Test")
        self.model.pk = ObjectId()

        self.emb_cls = TestEmbeddedDocument
        self.emb_model = TestEmbeddedDocument(title="Test")

        self.model.to_mongo = self.emb_model.to_mongo = lambda x: {
            "id": self.model.pk,
            "title": "Test"
        }

    @patch("json.dumps")
    def test_document(self, dumps):
        """self.model.to_json should call encode function."""
        self.model.to_json()
        dumps.assert_called_once_with(
            self.model.to_mongo(True), cls=GoodJSONEncoder
        )

    @patch("json.dumps")
    def test_embdocument(self, dumps):
        """self.emb_model.to_json should call encode function."""
        self.emb_model.to_json()
        dumps.assert_called_once_with(
            self.emb_model.to_mongo(True), cls=GoodJSONEncoder
        )


class FromJSONTest(TestCase):
    """object hook generation invocation test."""

    def setUp(self):
        """Setup the class."""
        import json

        class TestDocument(Document):
            title = db.StringField()

        class TestEmbeddedDocument(EmbeddedDocument):
            title = db.StringField()

        self.model_cls = TestDocument
        self.emb_cls = TestEmbeddedDocument
        self.data = json.dumps({"title": "Test"})

    @patch("mongoengine_goodjson.document.generate_object_hook")
    def test_document(self, hook_mock):
        """Document.from_json should call generate_object_hook."""
        hook_mock.return_value = lambda x: {"title": "Test"}
        self.model_cls.from_json(self.data)
        hook_mock.assert_called_once_with(self.model_cls)

    @patch("mongoengine_goodjson.document.generate_object_hook")
    def test_embdoc(self, hook_mock):
        """EmbeddedDocument.from_json should call generate_object_hook."""
        hook_mock.return_value = lambda x: {"title": "Test"}
        self.emb_cls.from_json(self.data)
        hook_mock.assert_called_once_with(self.emb_cls)
