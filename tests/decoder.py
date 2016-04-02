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
        self.expected_data = {"user": "56f63a716a8dec7705f36409"}
        self.data = json.dumps(self.expected_data)

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
        self.data = json.dumps({"user": "56f63a716a8dec7705f36409"})
        self.expected_data = {"user": ObjectId("56f63a716a8dec7705f36409")}

    def test_hook(self):
        """Given data should be decoded properly."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class DBRefDecodeTest(TestCase):
    """DBRef Test."""

    def setUp(self):
        """Setup class."""
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


class OidBasedReferenceDecodeTest(TestCase):
    """Object ID based reference decode test."""

    def setUp(self):
        """Setup class."""
        from bson import ObjectId

        class Source(db.Document):
            pass

        class Model(db.Document):
            src = db.ReferenceField(Source)

        self.src_cls = Source
        self.model_cls = Model
        self.src_id = ObjectId()
        self.data = json.dumps({
            "src": str(self.src_id)
        })
        self.expected_data = {"src": self.src_id}
        self.hook = generate_object_hook(self.model_cls)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class DateTimeEpochMillisecDecodeTest(TestCase):
    """DateTime epoch milliseconds Test."""

    def setUp(self):
        """Setup test."""
        from datetime import datetime, timedelta
        from calendar import timegm

        class DateTime(db.Document):
            date = db.DateTimeField()

        self.model_cls = DateTime
        now = datetime.utcnow()
        epoch_mil = int(timegm(now.timetuple())*1000 + now.microsecond / 1000)
        self.data = json.dumps({"date": epoch_mil})
        self.expected_data = {
            "date": datetime.utcfromtimestamp(
                        int(epoch_mil / 1000)
                    ) + timedelta(milliseconds=int(epoch_mil % 1000))
        }
        self.hook = generate_object_hook(self.model_cls)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class DateTimeISODecodeTest(TestCase):
    """DateTime ISO format Test."""

    def setUp(self):
        """Setup test."""
        from datetime import datetime
        from dateutil.parser import parse

        class DateTime(db.Document):
            date = db.DateTimeField()

        self.model_cls = DateTime
        now = datetime.utcnow()
        self.data = json.dumps({"date": now.isoformat()})
        self.expected_data = {"date": parse(now.isoformat())}
        self.hook = generate_object_hook(self.model_cls)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class DateTimeUnknownDecodeTest(TestCase):
    """DateTime unknown format Test."""

    def setUp(self):
        """Setup test."""
        from datetime import datetime

        class DateTime(db.Document):
            date = db.DateTimeField()

        self.model_cls = DateTime
        now = datetime.utcnow()

        # This format shouldn't be supported.
        self.data = json.dumps({"date": {
            "year": now.year,
            "month": now.month,
            "date": now.day
        }})
        self.hook = generate_object_hook(self.model_cls)

    def test_hook(self):
        """The hook should raise TypeError."""
        with self.assertRaises(TypeError) as e:
            json.loads(self.data, object_hook=self.hook)
        self.assertEqual(
            str(e.exception), "This type (dict) is not supported"
        )


class BinaryDecodeTest(TestCase):
    """Binary format test."""

    def setUp(self):
        """Setup test."""
        from base64 import b64encode, b64decode
        from bson.binary import Binary, BINARY_SUBTYPE

        class BinaryTest(db.Document):
            text = db.BinaryField()

        self.model_cls = BinaryTest
        self.data = {
            "text": {
                "data": b64encode(
                    ("This is a test").encode("utf-8")
                ).decode(),
                "type": BINARY_SUBTYPE
            }
        }
        self.expected_data = {
            "text": Binary(
                b64decode(self.data["text"]["data"]),
                self.data["text"]["type"]
            )
        }
        self.data = json.dumps(self.data)

        self.hook = generate_object_hook(BinaryTest)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)


class UUIDDecodeTest(TestCase):
    """UUID decode test."""

    def setUp(self):
        """Setup test."""
        from uuid import uuid5, NAMESPACE_DNS

        class UUIDModel(db.Document):
            uuid = db.UUIDField()

        self.model_cls = UUIDModel
        uuid = uuid5(NAMESPACE_DNS, "This is a test")
        self.expected_data = {
            "uuid": uuid
        }
        self.data = json.dumps({"uuid": str(uuid)})
        self.hook = generate_object_hook(UUIDModel)

    def test_hook(self):
        """The result of decode should be correct."""
        result = json.loads(self.data, object_hook=self.hook)
        self.assertDictEqual(self.expected_data, result)
