#!/usr/bin/env python
# coding=utf-8

"""FollowReferenceField to_mongo unit tests."""

from unittest import TestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from bson import DBRef, ObjectId, SON

from .schema import (
    DisabledIDCheckDocument, IDCheckDocument, ReferencedDocument
)


class FollowReferenceFieldIDCheckTest(TestCase):
    """Test case for FollowReferenceField ID check functionality."""

    def setUp(self):
        """Setup function."""
        self.referenced_doc = ReferencedDocument(name="hi")
        self.idcheck_doc = IDCheckDocument(ref=self.referenced_doc)

    @patch("mongoengine_goodjson.FollowReferenceField.error")
    def test_id_error(self, error):
        """Calling to_mongo without ID, the error function is called."""
        self.idcheck_doc.to_mongo()
        error.assert_called_once_with("The referenced document needs ID.")


class FollowReferenceFieldDisabledIDCheckTest(TestCase):
    """Test case for FollowReferenceField without id_check."""

    def setUp(self):
        """Setup function."""
        self.referenced_doc = ReferencedDocument(name="hi")
        self.doc = DisabledIDCheckDocument(ref=self.referenced_doc)

    @patch("mongoengine_goodjson.FollowReferenceField.error")
    def test_id(self, error):
        """Calling to_mongo without ID, the error isn't called."""
        self.doc.to_mongo()
        error.assert_not_called()


class FollowReferenceFieldNonDocumentCheckTest(TestCase):
    """Test case when the referenced data is not Document."""

    def setUp(self):
        """Setup."""
        self._id = ObjectId()
        self.doc = IDCheckDocument(
            ref=DBRef("referenced_document", self._id)
        )
        self.disabled_check = DisabledIDCheckDocument(
            ref=DBRef("referenced_document", self._id)
        )

    @patch("mongoengine.ReferenceField.to_mongo")
    def test_doc_check_enabled_idcheck(self, to_mongo):
        """ReferenceField.to_mongo should be called."""
        to_mongo.return_value = self._id
        ret_value = self.doc.to_mongo()
        self.assertTrue(to_mongo.called)
        self.assertDictEqual(SON({"ref": self._id}), ret_value)

    @patch("mongoengine.ReferenceField.to_mongo")
    def test_doc_check_enabled_nonidcheck(self, to_mongo):
        """ReferenceField.to_mongo should be called."""
        to_mongo.return_value = self._id
        ret_value = self.disabled_check.to_mongo()
        self.assertTrue(to_mongo.called)
        self.assertDictEqual(SON({"ref": self._id}), ret_value)
