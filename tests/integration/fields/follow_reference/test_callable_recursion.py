#!/usr/bin/env python
# coding=utf-8

"""Callable recursion tests."""

import json
try:
    from unittest.mock import MagicMock, call
except ImportError:
    from mock import MagicMock, call  # noqa
# from bson import ObjectId

import mongoengine_goodjson as gj
import mongoengine as db

from ....con_base import DBConBase


class CallableRecursionTests(DBConBase):
    """Callable recursion test."""

    def setUp(self):
        """Setup."""
        super(CallableRecursionTests, self).setUp()
        self.check_depth = MagicMock(
            side_effect=lambda doc, parent: doc.is_last
        )

        class TestDoc(gj.Document):
            """Test document."""

            name = db.StringField()
            is_last = db.BooleanField()
            ref = gj.FollowReferenceField(
                "self", max_depth=self.check_depth
            )

            def __str__(self):
                """Return stringified summary."""
                return ("TestDoc<ID: {}, is_last: {}, ref: {}>").format(
                    self.name, self.is_last, getattr(self.ref, "id", None)
                )

            def to_dict(self):
                """Return the dict."""
                return str(self.id) if self.is_last else {
                    "id": str(self.id),
                    "name": self.name,
                    "is_last": self.is_last,
                    "ref": self.ref.to_dict()
                }

        self.docs = [
            TestDoc.objects.create(
                name=("Test {}").format(count),
                is_last=(count == 4)
            ) for count in range(6)
        ]
        for (index, doc) in enumerate(self.docs):
            doc.ref = self.docs[(index + 1) % len(self.docs)]
            doc.save()

    def test_from_first(self):
        """Should encode the element from first to the element is_last=True."""
        max_depth_level = 5
        correct_data = self.docs[0].to_dict()
        actual_data = json.loads(self.docs[0].to_json())

        self.maxDiff = None
        self.assertEqual(correct_data, actual_data)
        self.check_depth.assert_has_calls([
            call(
                self.docs[count], self.docs[count - 1] if count > 0 else None
            ) for count in range(max_depth_level)
        ])
        self.assertEqual(self.check_depth.call_count, max_depth_level)
