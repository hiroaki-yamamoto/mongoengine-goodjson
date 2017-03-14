#!/usr/bin/env python
# coding=utf-8

"""Recursion Limit."""

import json

from unittest import skip

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import mongoengine_goodjson as gj
import mongoengine as db


from ....con_base import DBConBase
from ...fixtures.base import Dictable


class FollowReferenceFieldDefaultRecursionLimitTest(DBConBase):
    """Follow Reference Test Default Recusrion Test."""

    def setUp(self, **kwargs):
        """Setup."""
        self.maxDiff = None

        class ModelCls(Dictable, gj.Document):
            name = db.StringField()
            ref = gj.FollowReferenceField("self", **kwargs.copy())

        self.model_cls = ModelCls
        self.model = self.model_cls(name="test")
        self.model.save()
        self.model.ref = self.model
        self.model.save()

        self.data = self.model.to_dict(call_child_to_dict=False)
        cur_depth = self.data
        for index in range(kwargs.get("max_depth", 3) or 3):
            cur_depth["ref"] = cur_depth.copy()
            cur_depth = cur_depth["ref"]
        cur_depth["ref"] = self.data["id"]

    def tearDown(self):
        """Tear down class."""
        self.model_cls.objects.delete()

    def test_recursion_limit(self):
        """The result should have just 3-level depth."""
        result = json.loads(self.model.to_json())
        self.assertEqual(self.data, result)

    def test_decoder(self):
        """Test decoder."""
        self.model_cls.objects.delete()
        json_data = self.model.to_json()
        data = self.model_cls.from_json(self.model.to_json())
        self.assertEqual(json.loads(data.to_json()), json.loads(json_data))


class FollowReferenceFieldRecursionNoneTest(
    FollowReferenceFieldDefaultRecursionLimitTest
):
    """Follow Reference Test self recursion with None Test."""

    def setUp(self):
        """Setup."""
        super(FollowReferenceFieldRecursionNoneTest, self).setUp(
            max_depth=None
        )


class FollowReferenceFieldRecursionNumTest(
    FollowReferenceFieldDefaultRecursionLimitTest
):
    """Follow Reference Test self recursion with 5 recursions Test."""

    def setUp(self):
        """Setup."""
        super(FollowReferenceFieldRecursionNumTest, self).setUp(max_depth=5)


class FollowReferenceFieldNegativeRecursionTest(
    FollowReferenceFieldDefaultRecursionLimitTest
):
    """In the case of the max recursion level is negative."""

    @patch("mongoengine_goodjson.fields.follow_reference.log.warn")
    def setUp(self, warn):
        """Setup."""
        self.warn = warn
        super(FollowReferenceFieldNegativeRecursionTest, self).setUp(
            max_depth=-1
        )

    test_decoder = skip("Not needed")(lambda: None)

    def test_warning(self):
        """The warn should be shown."""
        self.warn.assert_called_once_with(
            "[BE CAREFUL!] Unlimited self reference might cause infinity loop!"
            " [BE CAREFUL!]"
        )

    def test_recursion_limit(self):
        """Should raise runtime error."""
        with self.assertRaises(RuntimeError):
            json.loads(self.model.to_json())
