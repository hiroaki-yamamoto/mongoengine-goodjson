#!/usr/bin/env python
# coding=utf-8

"""Complex Type Tests."""

import json

import mongoengine_goodjson as gj
import mongoengine as db

from ...fixtures.base import Dictable
from ....con_base import DBConBase


class FollowReferenceFieldLimitRecursionComlexTypeTest(DBConBase):
    """Follow reference field limit recursion with complex type test."""

    def setUp(self):
        """Setup."""
        class SubDocument(Dictable, gj.EmbeddedDocument):
            parent = gj.FollowReferenceField("MainDocument")
            ref_list = db.ListField(gj.FollowReferenceField("MainDocument"))

        class MainDocument(Dictable, gj.Document):
            name = db.StringField()
            ref_list = db.ListField(gj.FollowReferenceField("self"))
            subdoc = db.EmbeddedDocumentField(SubDocument)

        self.main_doc_cls = MainDocument
        self.sub_doc_cls = SubDocument
        self.main_docs = []

        for counter in range(4):
            main_doc = MainDocument(name=("Test {}").format(counter))
            main_doc.save()
            self.main_docs.append(main_doc)

        for (index, doc) in enumerate(self.main_docs):
            doc.subdoc = SubDocument(
                parent=doc, ref_list=[
                    doc, self.main_docs[index - 1],
                    self.main_docs[index - 2]
                ]
            )
            doc.ref_list.extend([
                doc, self.main_docs[index - 1], self.main_docs[index - 3]
            ])
            doc.save()

        self.expected_data = [doc.to_dict() for doc in self.main_docs]
        self.maxDiff = None

    def test_to_json(self):
        """The serialized json should be equal to the expected data."""
        result = [json.loads(item.to_json()) for item in self.main_docs]
        self.assertEqual(self.expected_data, result)
