#!/usr/bin/env python
# coding=utf-8

"""Simple Serialization Tests for FollowReferenceField."""

import json

from bson import ObjectId

from ...fixtures.user import (
    User, UserReferenceAutoSave, UserReferenceNoAutoSave,
    UserReferenceDisabledIDCheck
)
from ....con_base import DBConBase


class FollowReferenceFieldTest(DBConBase):
    """Follow reference field integration tests."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None
        self.RefDoc = User
        self.Doc = UserReferenceNoAutoSave
        self.AutoSaveDoc = UserReferenceAutoSave
        self.DocNoIDCheck = UserReferenceDisabledIDCheck
        self.ref_docs = [
            self.RefDoc.generate_test_data(counter)
            for counter in range(3)
        ]
        self.data_ref_docs = [ref_doc.to_dict() for ref_doc in self.ref_docs]
        self.doc = self.Doc()
        self.non_id_check_doc = self.DocNoIDCheck()
        self.autosave_doc = self.AutoSaveDoc()
        self.data = {
            u"id": str(ObjectId()),
            u"ref": {
                u"id": str(self.ref_docs[0].id),
                u"name": self.ref_docs[0].name,
                u"address": [],
                u"metadata": {},
            },
            u"refs": []
        }

    def tearDown(self):
        """Teardown class."""
        self.RefDoc.drop_collection()
        self.Doc.drop_collection()
        self.AutoSaveDoc.drop_collection()
        self.DocNoIDCheck.drop_collection()

    def test_serialization_with_save(self):
        """The serializer should follow the referenced doc."""
        for doc in self.ref_docs:
            doc.save()
        self.doc.ref = self.ref_docs[0]
        self.doc.refs = [
            doc for doc in self.ref_docs if doc != self.ref_docs[0]
        ]
        self.doc.save()

        result = json.loads(self.doc.to_json())
        self.assertDictEqual(self.doc.to_dict(), result)

    def test_serialization_without_save(self):
        """The serializer should follow the referenced doc (no ID check)."""
        self.non_id_check_doc.ref = self.ref_docs[0]
        result = json.loads(self.non_id_check_doc.to_json())
        self.assertDictEqual(self.non_id_check_doc.to_dict(), result)

    def test_serialization_with_follow_reference_true(self):
        """The serializer should work properly."""
        self.non_id_check_doc.ref = self.ref_docs[0]
        result = json.loads(
            self.non_id_check_doc.to_json(follow_reference=True)
        )
        self.assertDictEqual(self.non_id_check_doc.to_dict(), result)

    def test_deserialization_without_autosave(self):
        """The deserializer should work (no autosave)."""
        result = self.Doc.from_json(json.dumps(self.data))
        self.assertDictEqual(self.data, json.loads(result.to_json()))

    def test_deserialization_with_autosave(self):
        """The deserializer should work (autosave)."""
        result = self.AutoSaveDoc.from_json(json.dumps(self.data))
        self.assertDictEqual(self.data, json.loads(result.to_json()))
