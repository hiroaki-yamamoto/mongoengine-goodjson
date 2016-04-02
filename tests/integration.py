#!/usr/bin/env python
# coding=utf-8

"""Integration tests."""

from base64 import b64encode
from calendar import timegm
from datetime import datetime
import json
from unittest import TestCase
from uuid import uuid5, NAMESPACE_DNS

from bson import ObjectId
from bson.binary import Binary
import mongoengine as db
from mongoengine_goodjson import Document, EmbeddedDocument


class Address(EmbeddedDocument):
    """Test data."""

    street = db.StringField()
    city = db.StringField()
    state = db.StringField()


class User(Document):
    """Test data."""

    name = db.StringField()
    email = db.EmailField()
    address = db.EmbeddedDocumentListField(Address)


class Article(Document):
    """Test data."""

    user = db.ReferenceField(User)
    title = db.StringField()
    date = db.DateTimeField()
    body = db.BinaryField()
    uuid = db.UUIDField()


class ToJSONIntegrationTest(TestCase):
    """Good JSON Encoder Data test."""

    def setUp(self):
        """Setup the class."""
        self.now = datetime.utcnow()
        self.user_cls = User
        self.user = User(
            name="Test man", email="test@example.com",
            address=[
                Address(
                    street=("Test street %d" % counter),
                    city=("Test city %d" % counter),
                    state=("Test state %d" % counter)
                ) for counter in range(3)
            ]
        )
        self.user.pk = ObjectId()
        self.article_cls = Article
        self.article = Article(
            user=self.user, title="Test Tile", date=self.now,
            body=Binary(("This is a test body").encode()),
            uuid=uuid5(NAMESPACE_DNS, "This is a test")
        )
        self.article.pk = ObjectId()
        self.user_expected_data = {
            "id": str(self.user.pk),
            "name": self.user.name,
            "email": self.user.email,
            "address": [
                {
                    "street": "Test street %d" % counter,
                    "city": "Test city %d" % counter,
                    "state": "Test state %d" % counter
                } for counter in range(3)
            ]
        }
        self.article_expected_data = {
            "id": str(self.article.pk),
            "user": self.user_expected_data["id"],
            "title": self.article.title,
            "date": int(
                timegm(self.article.date.timetuple())*1000 +
                self.article.date.microsecond / 1000
            ),
            "body": {
                "data": b64encode(self.article.body).decode(),
                "type": self.article.body.subtype
            },
            "uuid": str(self.article.uuid)
        }

    def test_user_data(self):
        """User model should be encoded properly."""
        result = json.loads(self.user.to_json())
        self.assertDictEqual(self.user_expected_data, result)

    def test_article_data(self):
        """Article model should be encoded properly."""
        result = json.loads(self.article.to_json())
        self.assertDictEqual(self.article_expected_data, result)
