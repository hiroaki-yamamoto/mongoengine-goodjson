#!/usr/bin/env python
# coding=utf-8

"""Queryset tests."""

import json

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

import mongoengine as db
from mongoengine_goodjson import Document, QuerySet, GoodJSONEncoder

from .connection_case import DBConBase


class QuerysetEncodeDecodeTest(DBConBase):
    """Queryset encoding / decoding tests."""

    def setUp(self):
        """Setup the class."""
        self.dict_model = [
            {u"test": u"Hello %s" % count} for count in range(5)
        ]
        QuerySet.as_pymongo = MagicMock(return_value=self.dict_model)

        class TestModel(Document):
            test = db.StringField()

        self.as_pymongo = TestModel.objects.as_pymongo
        self.model_cls = TestModel
        self.model = [
            self.model_cls(test="Hello %s" % count) for count in range(5)
        ]

    @patch("json.dumps")
    def test_encode(self, dumps):
        """The encode functionality should call proper-funcitons."""
        self.model_cls.objects.to_json(indent=2)
        self.as_pymongo.assert_called_once_with()
        dumps.assert_called_once_with(
            self.as_pymongo.return_value,
            cls=GoodJSONEncoder, indent=2
        )

    @patch("json.loads")
    @patch("mongoengine_goodjson.queryset.generate_object_hook")
    def test_decode(self, gen_obj_hook, loads):
        """The decode funcitonality should call proper-functions."""
        gen_obj_hook.return_value = lambda x: {"test": "Hello"}
        json_str = json.dumps(self.dict_model)
        self.model_cls.objects.from_json(json_str)
        gen_obj_hook.assert_called_once_with(self.model_cls)
        loads.assert_called_once_with(
            json_str, object_hook=gen_obj_hook.return_value
        )
