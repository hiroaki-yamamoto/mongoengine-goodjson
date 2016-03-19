#!/usr/bin/env python
# coding=utf-8

from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from mongoengine_goodjson import GoodJSONEncoder


class NormalStuffEncodingTest(TestCase):
    """Normal stuff should be encoded."""

    def setUp(self):
        """Setup function."""
        self.encoder = GoodJSONEncoder()
        self.data = "test"

    @patch("json.JSONEncoder.default")
    def test_json_encoder(self, default):
        """The default json encoder should be called."""
        self.encoder.default(self.data)
        default.assert_called_once_with(self.data)


class ObjectIdEncodeTest(TestCase):
    """Object ID Encoding test."""

    def setUp(self):
        """Setup function."""
        from bson import ObjectId
        self.encoder = GoodJSONEncoder()
        self.oid = ObjectId()

    def test_object_id(self):
        """encoder should return the object id as str"""
        result = self.encoder.default(self.oid)
        self.assertEqual(result, str(self.oid))


class DatetimeEncodeTest(TestCase):
    """datetime encoding test"""

    def setUp(self):
        """Setup funciton."""
        from datetime import datetime
        self.now = datetime.utcnow()
        self.encoder = GoodJSONEncoder()

    def test_datetime(self):
        """datetime should be serialized into epoch millisecond"""
        from calendar import timegm
        self.assertEqual(
            self.encoder.default(self.now),
            int(
                timegm(self.now.timetuple()) * 1000 +
                self.now.microsecond / 1000
            )
        )


class DBRefEncodingTestBase(TestCase):
    """DBRef test case base."""

    def setUp(self):
        """Setup function."""
        from bson.dbref import DBRef
        from bson import ObjectId
        self.DBRef = DBRef
        self.encoder = GoodJSONEncoder()
        self.custom_argument = {
            "test key %d" % counter: "Test value %d" % counter
            for counter in range(3)
        }
        self.collection_name = "test.collection"
        self.doc_id = ObjectId()
        self.database = "test.db"


class DBRefEncodeWithDBTest(DBRefEncodingTestBase):
    """DBRef with external database encoding test."""

    def setUp(self):
        """Setup function."""
        super(DBRefEncodeWithDBTest, self).setUp()
        self.data = self.DBRef(
            self.collection_name, self.doc_id,
            database=self.database, **self.custom_argument
        )
        self.expected_result = {
            "collection": self.collection_name,
            "db": self.database,
            "id": self.encoder.default(self.doc_id)
        }
        self.expected_result.update(self.custom_argument)

    def test_dbref(self):
        """DBRef test."""
        self.assertDictEqual(
            self.expected_result, self.encoder.default(self.data)
        )
