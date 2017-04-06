#!/usr/bin/env python
# coding=utf-8

"""Queryset integration tests."""

import json

import mongoengine_goodjson as gj
import mongoengine as db

from .fixtures.base import Dictable
from .fixtures.user import User, UserReferenceNoAutoSave
from ..con_base import DBConBase


# class EmptyEuqeyTest(DBConBase):
#     """Empty query test."""
#
#     def test_to_json(self):
#         """The serialized value should be an empty list."""
#         self.assertEqual(json.loads(User.objects.to_json()), [])


class UserSerializationDesrializationTest(DBConBase):
    """User serialization / deserialization integration test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None
        User.objects.delete()
        self.users = [User.generate_test_data(counter) for counter in range(3)]
        self.users_dict = [item.to_dict() for item in self.users]
        for user_el in self.users:
            user_el.save()

    def test_encode(self):
        """The data should be encoded properly."""
        result = json.loads(User.objects.to_json())
        self.assertEqual(
            sorted(result, key=lambda obj: obj["id"]),
            sorted(self.users_dict, key=lambda obj: obj["id"])
        )

    def test_decode(self):
        """The data should be decoded properly."""
        result = User.objects.from_json(json.dumps(self.users_dict))
        self.assertEqual(self.users, result)

    def test_as_pymongo(self):
        """Should behave as normal."""
        data = []
        for item in self.users:
            el = item.to_dict(oid_as_str=False, call_child_to_dict=False)
            el["_id"] = el.pop("id")
            data.append(el)
        actual = User.objects.as_pymongo()
        self.assertEqual(data, list(actual))


class QuerySetJSONExclusionTest(DBConBase):
    """JSON exclusion test (Queryset version)."""

    def setUp(self):
        """Setup."""
        class ExclusionModel(gj.Document):
            to_json_exclude = db.StringField(exclude_to_json=True)
            from_json_exclude = db.IntField(exclude_from_json=True)
            json_exclude = db.StringField(exclude_json=True)
            required = db.StringField(required=True)

        self.cls = ExclusionModel
        self.test_data = []
        for counter in range(3):
            data_el = {
                "to_json_exclude": ("To JSON Exclusion {}").format(counter),
                "from_json_exclude": counter,
                "json_exclude": ("JSON Exclusion {}").format(counter),
                "required": ("Required {}").format(counter)
            }
            model = self.cls(**data_el)
            model.save()
            self.test_data.append(data_el)

    def test_encode(self):
        """to_json_exclude and json_exclude shouldn't be in the result."""
        result = json.loads(self.cls.objects.to_json())
        for index, item in enumerate(result):
            self.assertNotIn(
                "to_json_exclude", item,
                ("to_json_exclude found at index {}").format(index)
            )
            self.assertNotIn(
                "json_exclude", item,
                ("json_exclude found at index {}").format(index)
            )
            self.assertIn(
                "from_json_exclude", item,
                ("from_json_exclude not found at index {}").format(index)
            )
            self.assertIn(
                "required", item,
                ("required not found at index {}").format(index)
            )

    def test_decode(self):
        """from_json_exclude and json_exclude shouldn't put into the model."""
        models = self.cls.objects.from_json(json.dumps(self.test_data))
        for index, model in enumerate(models):
            self.assertIsNone(
                model.json_exclude,
                ("json_exclude found at index {}").format(index)
            )
            self.assertIsNone(
                model.from_json_exclude,
                ("from_json_exclude found at index {}").format(index)
            )
            self.assertIsNotNone(
                model.to_json_exclude,
                ("to_json_exclude not found at index {}").format(index)
            )
            self.assertIsNotNone(
                model.required,
                ("required not found at index {}").format(index)
            )


class FollowReferenceQueryTest(DBConBase):
    """FollowReferenceQuery Test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None
        self.users = [User.generate_test_data(counter) for counter in range(3)]
        self.data_users = [item.to_dict() for item in self.users]
        self.refs = []
        self.data_ref_users = []

        for (index, user) in enumerate(self.users):
            user.save()
            ref = UserReferenceNoAutoSave(
                ref=user,
                refs=[ruser for ruser in self.users if ruser != user]
            )
            ref.save()
            self.refs.append(ref)
            self.data_ref_users.append({
                u"id": str(ref.id),
                u"ref": self.data_users[index],
                u"refs": [
                    duser for duser in self.data_users
                    if duser != self.data_users[index]
                ]
            })

    def test_to_json(self):
        """The document referenced by the field should be referenced."""
        result = json.loads(UserReferenceNoAutoSave.objects.to_json())
        self.assertListEqual(result, self.data_ref_users)


class PartialQuerySetReferenceTest(DBConBase):
    """Partial query set reference test."""

    def setUp(self):
        """Setup."""
        super(PartialQuerySetReferenceTest, self).setUp()

        class Doc(Dictable, gj.Document):
            """Document."""

            test1 = db.StringField()
            test2 = db.StringField()
            test3 = db.StringField()
            test4 = db.IntField()

        self.doc_cls = Doc
        self.docs = [
            self.doc_cls.objects.create(test1="TEST1"),
            self.doc_cls.objects.create(test1="TEST2", test2="tEsT2"),
            self.doc_cls.objects.create(test1="TEST3", test3="tEsT3")
        ]

    def tearDown(self):
        """Tear down."""
        self.doc_cls.drop_collection()
        super(PartialQuerySetReferenceTest, self).tearDown()

    def test_encode(self):
        """The serialized document should be expected."""
        data = [item.to_dict() for item in self.docs[0:2]]
        actual = self.doc_cls.objects[0:2]
        self.assertEqual(
            json.loads(actual.to_json()), data
        )

    def test_as_pymongo(self):
        """Should behave as normal."""
        data = []
        self.maxDiff = None
        for item in self.docs[0:2]:
            el = item.to_dict(oid_as_str=False, call_child_to_dict=False)
            el["_id"] = el.pop("id")
            data.append(el)
        actual = self.doc_cls.objects[0:2].as_pymongo()
        self.assertEqual(data, list(actual))


class NotInheritGJDocTest(DBConBase):
    """QuerySet that is embedded to the normal doc reference test."""

    def setUp(self):
        """Setup."""
        super(NotInheritGJDocTest, self).setUp()

        class Doc(Dictable, db.Document):
            """Document."""

            meta = {"queryset_class": gj.QuerySet}

            test1 = db.StringField()
            test2 = db.StringField()
            test3 = db.StringField()
            test4 = db.IntField()

        self.doc_cls = Doc
        self.docs = [
            self.doc_cls.objects.create(test1="TEST1"),
            self.doc_cls.objects.create(test1="TEST2", test2="tEsT2"),
            self.doc_cls.objects.create(test1="TEST3", test3="tEsT3")
        ]

    def tearDown(self):
        """Tear down."""
        self.doc_cls.drop_collection()
        super(NotInheritGJDocTest, self).tearDown()

    def test_encode(self):
        """The queryset should behave as usual."""
        data = [json.loads(item.to_json()) for item in self.docs]
        self.assertEqual(
            json.loads(self.doc_cls.objects.to_json()), data
        )
