#!/usr/bin/env python
# coding=utf-8

"""Test list recursion."""

import json
from bson import ObjectId

import mongoengine_goodjson as gj
import mongoengine as db

from ...fixtures.base import Dictable
from ....con_base import DBConBase


class FollowReferenceFieldListRecursionTest(DBConBase):
    """Follow Reference Field List Recursion test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None

        class Ref1(Dictable, gj.Document):
            ref1_name = db.StringField()

            @classmethod
            def generate_test_data(cls, count):
                ret = cls(ref1_name=("Test {}").format(count))
                ret.save()
                return ret

        class Ref2(Dictable, gj.Document):
            ref2_refs = db.ListField(gj.FollowReferenceField(Ref1))

            @classmethod
            def generate_test_data(cls, refs):
                ret = cls(ref2_refs=refs)
                ret.save()
                return ret

        class Ref25(Dictable, gj.EmbeddedDocument):
            ref25_ref = gj.FollowReferenceField(Ref2)
            ref25_refs = db.ListField(gj.FollowReferenceField(Ref2))

            @classmethod
            def generate_test_data(cls, ref, refs):
                ret = cls(ref25_ref=ref, ref25_refs=refs)
                return ret

        class Ref3(Dictable, gj.Document):
            ref3_ref = gj.FollowReferenceField(Ref2)
            ref3_refs = db.ListField(gj.FollowReferenceField(Ref2))
            ref3_emb = db.EmbeddedDocumentField(Ref25)
            ref3_embs = db.EmbeddedDocumentListField(Ref25)
            ref3_oids = db.ListField(db.ObjectIdField(), default=[
                ObjectId() for ignore in range(3)
            ])

            @classmethod
            def generate_test_data(cls, emb, embs, oids, ref, refs):
                ret = cls(
                    ref3_emb=emb, ref3_embs=embs, ref3_oids=oids,
                    ref3_ref=ref, ref3_refs=refs
                )
                ret.save()
                return ret

        self.ref1_cls = Ref1
        self.ref2_cls = Ref2
        self.ref25_cls = Ref25
        self.ref3_cls = Ref3

        self.ref1 = [
            self.ref1_cls.generate_test_data(count) for count in range(3)
        ]
        self.ref2 = [
            self.ref2_cls.generate_test_data([
                item for item in self.ref1
                if item != ref1
            ]) for ref1 in self.ref1
        ]
        self.ref25 = [
            self.ref25_cls.generate_test_data(
                ref2, [data for data in self.ref2 if data != ref2]
            ) for ref2 in self.ref2
        ]
        self.ref3 = [
            self.ref3_cls.generate_test_data(
                ref25,
                [data for data in self.ref25 if data != ref25],
                [ObjectId() for ignore in range(4)],
                ref2, [item for item in self.ref2 if item != ref2]
            )
            for (ref2, ref25) in [
                (self.ref2[index], self.ref25[index])
                for index in range(min([len(self.ref2), len(self.ref25)]))
            ]
        ]

    def tearDown(self):
        """Teardown."""
        self.ref1_cls.objects().delete()
        self.ref2_cls.objects().delete()
        self.ref3_cls.objects().delete()

    def test_to_json(self):
        """Test to_json."""
        results = [
            json.loads(item.to_json())
            for item in self.ref3_cls.objects()
        ]
        self.assertEqual(
            sorted(results, key=lambda obj: obj["id"]),
            sorted(
                [ref3.to_dict() for ref3 in self.ref3],
                key=lambda obj: obj["id"]
            )
        )

    def test_from_json(self):
        """Test from_json."""
        self.ref1_cls.objects().delete()
        self.ref2_cls.objects().delete()
        self.ref3_cls.objects().delete()
        results = [
            json.loads(self.ref3_cls.from_json(item.to_json()).to_json())
            for item in self.ref3
        ]
        expected = [json.loads(item.to_json()) for item in self.ref3]
        self.assertEqual(results, expected)
