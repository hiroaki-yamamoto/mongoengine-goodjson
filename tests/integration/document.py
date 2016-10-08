#!/usr/bin/env python
# coding=utf-8

"""Integration tests."""

import json
from unittest import TestCase

from bson import ObjectId
import mongoengine_goodjson as gj
import mongoengine as db

from .schema import (
    User, Article, Email, Reference, UserReferenceNoAutoSave,
    UserReferenceAutoSave, UserReferenceDisabledIDCheck
)
from .fixtures import (
    user, user_dict, article, article_dict, article_dict_epoch,
    email, email_dict_id, email_dict_email, reference, reference_dict
)
from ..connection_case import DBConBase

try:
    str = unicode
except NameError:
    pass


class ToJSONNormalIntegrationTest(TestCase):
    """Good JSON Encoder Normal Data test."""

    def setUp(self):
        """Setup the class."""
        self.maxDiff = None
        self.user_cls = User
        self.user = user
        self.article_cls = Article
        self.article = article
        self.user_dict = user_dict
        self.article_dict = article_dict
        self.article_dict_epoch = article_dict_epoch

    def test_encode_user_data(self):
        """User model should be encoded properly."""
        result = json.loads(self.user.to_json())
        self.assertDictEqual(self.user_dict, result)

    def test_encode_article_data(self):
        """Article model should be encoded properly."""
        result = json.loads(self.article.to_json())
        self.assertDictEqual(self.article_dict, result)

    def test_encode_article_data_epoch_flag(self):
        """Article model should be encoded properly (Epoch flag is on)."""
        result = json.loads(self.article.to_json(epoch_mode=True))
        self.assertDictEqual(self.article_dict_epoch, result)

    def test_decode_user_data(self):
        """The decoded user data should be self.user."""
        user = self.user_cls.from_json(json.dumps(self.user_dict))
        self.assertIs(type(user), self.user_cls)
        self.assertDictEqual(self.user.to_mongo(), user.to_mongo())

    def test_decode_article_data(self):
        """The decoded user data should be self.user."""
        article = self.article_cls.from_json(json.dumps(self.article_dict))
        self.assertIs(type(article), self.article_cls)
        self.assertDictEqual(self.article.to_mongo(), article.to_mongo())

    def test_decode_article_data_epoch(self):
        """The decoded user data should be self.article."""
        article = self.article_cls.from_json(
            json.dumps(self.article_dict_epoch)
        )
        self.assertIs(type(article), self.article_cls)
        self.assertDictEqual(self.article.to_mongo(), article.to_mongo())


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


class FollowReferenceTest(DBConBase):
    """Good JSON follow reference encoder/decoder test."""

    def setUp(self):
        """Setup function."""
        self.maxDiff = None
        self.reference_cls = Reference
        self.reference = reference
        self.reference_dict = reference_dict

    def test_encode_follow_reference_data(self):
        """Reference data should follow ReferenceField."""
        result = json.loads(self.reference.to_json(follow_reference=True))
        self.assertDictEqual(self.reference_dict, result)

    def test_decode_reference(self):
        """The decoded reference data should be self.reference."""
        result = self.reference_cls.from_json(
            json.dumps(self.reference_dict)
        )
        self.assertIs(type(result), self.reference_cls)
        self.assertEqual(result.id, self.reference.id)
        self.assertEqual(result.name, self.reference.name)
        self.assertListEqual(self.reference.references, result.references)

    def test_actual_data_store(self):
        """Actually data store."""
        for ref in self.reference.references:
            ref.user.save()
            ref.save()
        self.reference.save(cascade=True)
        result = json.loads(
            self.reference_cls.objects(
                id=self.reference.id
            ).get().to_json(follow_reference=True)
        )
        print(self.reference_dict)
        self.assertDictEqual(self.reference_dict, result)


class PrimaryKeyNotOidTest(TestCase):
    """Good JSON encoder/decoder email as primary key test."""

    def setUp(self):
        """Setup the class."""
        self.email = email
        self.data_id = email_dict_id
        self.data_email = email_dict_email

    def test_encode(self):
        """Email document should be encoded properly."""
        result = json.loads(self.email.to_json())
        self.assertDictEqual(self.data_id, result)

    def test_decode_id(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "id" field.
        """
        result = Email.from_json(json.dumps(self.data_id)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)

    def test_decode_email(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "email" field.
        """
        result = Email.from_json(json.dumps(self.data_email)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)


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
            self.RefDoc(
                id=ObjectId(),
                name=("Test {}").format(counter)
            ) for counter in range(3)
        ]
        self.data_ref_docs = [
            {u"id": str(ref_doc.id), u"name": ref_doc.name, u"address": []}
            for ref_doc in self.ref_docs
        ]
        self.doc = self.Doc()
        self.non_id_check_doc = self.DocNoIDCheck()
        self.autosave_doc = self.AutoSaveDoc()
        self.data = {
            u"id": str(ObjectId()),
            u"ref": {
                u"id": str(self.ref_docs[0].id),
                u"name": self.ref_docs[0].name,
                u"address": [],
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
        self.assertDictEqual({
            u"id": str(self.doc.pk),
            u"ref": {
                u"id": str(self.ref_docs[0].pk),
                u"name": self.ref_docs[0].name,
                u"address": []
            },
            u"refs": [
                d for d in self.data_ref_docs if d != self.data_ref_docs[0]
            ]
        }, result)

    def test_serialization_without_save(self):
        """The serializer should follow the referenced doc (no ID check)."""
        self.non_id_check_doc.ref = self.ref_docs[0]
        result = json.loads(self.non_id_check_doc.to_json())
        self.assertDictEqual({
            u"ref": {
                u"id": str(self.ref_docs[0].id),
                u"name": self.ref_docs[0].name,
                u"address": []
            },
            u"refs": []
        }, result)

    def test_serialization_with_follow_reference_true(self):
        """The serializer should work properly."""
        self.non_id_check_doc.ref = self.ref_docs[0]
        result = json.loads(
            self.non_id_check_doc.to_json(follow_reference=True)
        )
        self.assertDictEqual({
            u"ref": {
                u"id": str(self.ref_docs[0].id),
                u"name": self.ref_docs[0].name,
                u"address": []
            },
            u"refs": []
        }, result)

    def test_deserialization_without_autosave(self):
        """The deserializer should work (no autosave)."""
        result = self.Doc.from_json(json.dumps(self.data))
        self.assertDictEqual(self.data, json.loads(result.to_json()))

    def test_deserialization_with_autosave(self):
        """The deserializer should work (autosave)."""
        result = self.AutoSaveDoc.from_json(json.dumps(self.data))
        self.assertDictEqual(self.data, json.loads(result.to_json()))


class FollowReferenceFieldListRecursionTest(DBConBase):
    """Follow Reference Field List Recursion test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None

        class Ref1(gj.Document):
            name = db.StringField()

        class Ref2(gj.Document):
            refs = db.ListField(gj.FollowReferenceField(Ref1))

        class Ref25(gj.EmbeddedDocument):
            ref = gj.FollowReferenceField(Ref2)
            refs = db.ListField(gj.FollowReferenceField(Ref2))

        class Ref3(gj.Document):
            ref = gj.FollowReferenceField(Ref2)
            refs = db.ListField(gj.FollowReferenceField(Ref2))
            emb = db.EmbeddedDocumentField(Ref25)
            embs = db.EmbeddedDocumentListField(Ref25)
            oids = db.ListField(db.ObjectIdField(), default=[
                ObjectId for ignore in range(3)
            ])

        self.ref1_cls = Ref1
        self.ref2_cls = Ref2
        self.ref3_cls = Ref3

        self.data_ref1 = [
            {
                "id": str(ObjectId()),
                "name": ("Test {}").format(counter)
            } for counter in range(3)
        ]
        self.data_ref2 = [
            {
                "id": str(ObjectId()),
                "refs": [
                    item for (index, item) in enumerate(self.data_ref1)
                    if index != counter
                ]
            } for counter in range(len(self.data_ref1))
        ]
        self.instance_data_ref2 = [
            {
                "id": ref2["id"],
                "refs": [item["id"] for item in ref2["refs"]]
            } for ref2 in self.data_ref2
        ]
        self.data_ref25 = [
            {
                "ref": self.data_ref2[counter],
                "refs": [
                    data for (index, data) in enumerate(self.data_ref2)
                    if index != counter
                ]
            } for counter in range(len(self.data_ref2))
        ]
        self.instance_data_ref25 = [
            {
                "ref": ref["ref"]["id"],
                "refs": [data["id"] for data in ref["refs"]]
            } for ref in self.data_ref25
        ]
        self.data_ref3 = [
            {
                "id": str(ObjectId()),
                "ref": self.data_ref2[counter],
                "refs": [
                    item for (index, item) in enumerate(self.data_ref2)
                    if index != counter
                ],
                "oids": [str(ObjectId()) for ignore in range(4)],
                "emb": self.data_ref25[counter],
                "embs": [
                    data for (index, data) in enumerate(self.data_ref25)
                    if index != counter
                ]
            } for counter in range(len(self.data_ref2))
        ]
        self.instance_data_ref3 = [
            {
                k: ([el["id"] for el in v] if isinstance(v, list) else v["id"])
                if v in ["ref", "refs"] else v
                for (k, v) in item.items()
            } for item in self.data_ref3
        ]

    def test_to_json(self):
        """Test to_json."""
        for item in self.data_ref1:
            self.ref1_cls(**item).save()
        for item in self.instance_data_ref2:
            self.ref2_cls(**item).save()
        for item in self.instance_data_ref3:
            self.ref3_cls(**item).save()
        results = [
            json.loads(item.to_json())
            for item in self.ref3_cls.objects()
        ]
        self.assertSequenceEqual(
            sorted(results, key=lambda obj: obj["id"]),
            sorted(self.data_ref3, key=lambda obj: obj["id"])
        )
