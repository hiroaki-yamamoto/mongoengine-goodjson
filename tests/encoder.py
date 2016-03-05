#!/usr/bin/env python
# coding=utf-8

from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from mongoengine_goodjson import GoodJSONEncoder


class NormalStuffEncodingTest(TestCase):
    '''
    Normal stuff should be encoded
    '''

    def setUp(self):
        self.encoder = GoodJSONEncoder()
        self.data = "test"

    @patch("json.JSONEncoder.default")
    def test_json_encoder(self, default):
        '''
        The default json encoder should be called when an object that is not
        listed on singledispatcher is passed.
        '''
        self.encoder.default(self.data)
        default.assert_called_once_with(self.data)


class ObjectIdEncodeTest(TestCase):
    '''
    Object ID Encoding test
    '''

    def setUp(self):
        from bson import ObjectId
        self.encoder = GoodJSONEncoder()
        self.oid = ObjectId()

    def test_object_id(self):
        '''
        encoder should return the object id as str
        '''
        result = self.encoder.default(self.oid)
        self.assertEqual(result, str(self.oid))


class DatetimeEncodeTest(TestCase):
    '''
    datetime encoding test
    '''
    def setUp(self):
        from datetime import datetime
        self.now = datetime.utcnow()
        self.encoder = GoodJSONEncoder()

    def test_datetime(self):
        '''
        datetime should be serialized into epoch millisecond
        '''
        from time import mktime
        self.assertEqual(
            self.encoder.default(self.now),
            int(
                mktime(self.now.timetuple()) * 1000 +
                self.now.microsecond / 1000
            )
        )
