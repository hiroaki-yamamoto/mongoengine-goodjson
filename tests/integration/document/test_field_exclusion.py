#!/usr/bin/env python
# coding=utf-8

"""Field exclusion tests."""

import json
import mongoengine_goodjson as gj
import mongoengine as db

from ...con_base import DBConBase


class JSONExclusionTest(DBConBase):
    """JSON Exclusion Test."""

    def setUp(self):
        """Setup."""
        class ExclusionModel(gj.Document):
            to_json_exclude = db.StringField(exclude_to_json=True)
            from_json_exclude = db.IntField(exclude_from_json=True)
            json_exclude = db.StringField(exclude_json=True)
            required = db.StringField(required=True)

        self.cls = ExclusionModel
        self.data = {
            "to_json_exclude": "Hello",
            "from_json_exclude": 10234,
            "json_exclude": "Hi",
            "required": "World"
        }
        self.model = self.cls(**self.data)

    def test_to_json(self):
        """to_json_exclude and json_exclude shouldn't be in the output data."""
        result = json.loads(self.model.to_json())
        self.assertNotIn("to_json_exclude", result)
        self.assertNotIn("json_exclude", result)
        self.assertIn("from_json_exclude", result)
        self.assertIn("required", result)

    def test_from_json(self):
        """from_json_exclude and json_exclude shouldn't be decoded."""
        result = self.cls.from_json(json.dumps(self.data))
        self.assertIsNone(result.from_json_exclude)
        self.assertIsNone(result.json_exclude)
        self.assertIsNotNone(result.to_json_exclude)
        self.assertIsNotNone(result.required)
