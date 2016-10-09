#!/usr/bin/env python
# coding=utf-8

"""FollowReferenceField to_mongo unit tests."""

from unittest import TestCase

try:
    from unittest.mock import patch, PropertyMock
except ImportError:
    from mock import patch, PropertyMock

from bson import DBRef, ObjectId, SON

from .schema import (
    DisabledIDCheckDocument, IDCheckDocument, ReferencedDocument
)
from ..connection_case import DBConBase


class FollowReferenceFieldIDCheckTest(TestCase):
    """Test case for FollowReferenceField ID check functionality."""

    def setUp(self):
        """Setup function."""
        self.referenced_doc = ReferencedDocument(name="hi")
        self.idcheck_doc = IDCheckDocument(
            enable_gj=True,
            ref=self.referenced_doc
        )

    @patch("mongoengine_goodjson.FollowReferenceField.error")
    def test_id_error(self, error):
        """Calling to_mongo without ID, the error function is called."""
        self.idcheck_doc.to_mongo()
        error.assert_called_once_with("The referenced document needs ID.")

    @patch("mongoengine.ReferenceField.to_mongo")
    def test_tomongo_not_called(self, ref_to_mongo):
        """to_mongo shouldn't be called."""
        self.referenced_doc.pk = ObjectId()
        self.idcheck_doc.to_mongo()
        ref_to_mongo.assert_not_called()


class FollowReferenceFieldDisabledIDCheckTest(TestCase):
    """Test case for FollowReferenceField without id_check."""

    def setUp(self):
        """Setup function."""
        self.referenced_doc = ReferencedDocument(name="hi")
        self.doc = DisabledIDCheckDocument(
            ref=self.referenced_doc, enable_gj=True
        )

    @patch("mongoengine_goodjson.FollowReferenceField.error")
    def test_id(self, error):
        """Calling to_mongo without ID, the error isn't called."""
        self.doc.to_mongo()
        error.assert_not_called()

    @patch("mongoengine.ReferenceField.to_mongo")
    def test_tomongo_not_called(self, to_mongo):
        """to_mongo shouldn't be called."""
        self.doc.to_mongo()
        to_mongo.assert_not_called()


class FollowReferenceFieldNonDocumentCheckTest(DBConBase):
    """Test case when the referenced data is not Document."""

    def setUp(self):
        """Setup."""
        self._id = ObjectId()
        self.doc = IDCheckDocument(ref=DBRef("referenced_document", self._id))
        self.disabled_check = DisabledIDCheckDocument(
            enable_gj=True, ref=DBRef("referenced_document", self._id)
        )

    @patch("mongoengine.ReferenceField.to_mongo")
    @patch(
        "mongoengine_goodjson.FollowReferenceField.document_type",
        new_callable=PropertyMock
    )
    def test_doc_check_enabled_idcheck(self, doc_type, to_mongo):
        """ReferenceField.to_mongo should be called."""
        self.doc.to_mongo()
        self.assertTrue(to_mongo.called)

    @patch("mongoengine.ReferenceField.to_mongo")
    @patch(
        "mongoengine_goodjson.FollowReferenceField.document_type",
        new_callable=PropertyMock
    )
    def test_doc_check_enabled_nonidcheck(self, doc_type, to_mongo):
        """ReferenceField.to_mongo should be called."""
        doc_type.new_callable = PropertyMock
        self.disabled_check.to_mongo()
        self.assertTrue(to_mongo.called)


class FollowReferenceFieldReturnValueTest(DBConBase):
    """Test case for return value."""

    def setUp(self):
        """Setup."""
        self.referenced_doc = ReferencedDocument(name="hi")
        self.referenced_doc.save()
        self.doc = IDCheckDocument(ref=self.referenced_doc)
        self.ref_doc = IDCheckDocument(
            enable_gj=True,
            ref=DBRef("referenced_document", self.referenced_doc.pk)
        )

    def test_return_value_doc(self):
        """The return value from Doc should be proper."""
        ret = self.doc.to_mongo()
        self.assertDictEqual(
            SON({"ref": {"_id": self.referenced_doc.id, "name": "hi"}}), ret
        )

    def test_return_value_ref(self):
        """The return value from Ref should be proper."""
        ret = self.ref_doc.to_mongo()
        self.assertDictEqual(
            SON({"ref": {"_id": self.referenced_doc.id, "name": "hi"}}), ret
        )
