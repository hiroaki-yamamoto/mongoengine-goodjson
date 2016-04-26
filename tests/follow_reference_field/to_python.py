#!/usr/bin/env python
# coding=utf-8

"""ReferenceField.to_python tests."""

from unittest import TestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from bson import ObjectId

import mongoengine_goodjson as gj

from .schema import ReferencedDocument


class FollowReferenceFieldWithIDTest(TestCase):
    """Unit tests for Follow Reference Field with ID."""

    def setUp(self):
        """Setup function."""
        self.RefDoc = ReferencedDocument
        self.ref_doc = self.RefDoc(name="Test")
        self.ref_doc.pk = ObjectId()

    @patch("mongoengine.ReferenceField.to_python")
    def test_super_function_call(self, to_python):
        """ReferenceField.to_python should be called."""
        gj.FollowReferenceField(self.RefDoc).to_python(self.ref_doc)
        self.assertTrue(to_python.called)


class FollowReferenceFieldWithoutIDTest(TestCase):
    """Unit test for Follow Reference Field WITHOUT ID."""

    def setUp(self):
        """Setup function."""
        self.RefDoc = ReferencedDocument
        self.ref_doc = self.RefDoc(name="Test")
