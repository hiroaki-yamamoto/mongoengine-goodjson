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

try:
    str = unicode
except NameError:
    pass


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
        self.maxDiff = None
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
            body=Binary(b"\x00\x01\x02\x03\x04"),
            uuid=uuid5(NAMESPACE_DNS, "This is a test")
        )
        self.article.pk = ObjectId()
        self.user_expected_data = {
            u"id": str(self.user.pk),
            u"name": self.user.name,
            u"email": self.user.email,
            u"address": [
                {
                    u"street": "Test street %d" % counter,
                    u"city": "Test city %d" % counter,
                    u"state": "Test state %d" % counter
                } for counter in range(3)
            ]
        }
        self.article_expected_data = {
            u"id": str(self.article.pk),
            u"user": self.user_expected_data["id"],
            u"title": self.article.title,
            u"date": int(
                timegm(self.article.date.timetuple())*1000 +
                self.article.date.microsecond / 1000
            ),
            u"body": {
                u"data": str(b64encode(self.article.body).decode("utf-8")),
                u"type": self.article.body.subtype
            },
            u"uuid": str(self.article.uuid)
        }

    def test_user_data(self):
        """User model should be encoded properly."""
        result = json.loads(self.user.to_json())
        self.assertDictEqual(self.user_expected_data, result)

    def test_article_data(self):
        """Article model should be encoded properly."""
        result = json.loads(self.article.to_json())
        self.assertDictEqual(self.article_expected_data, result)
