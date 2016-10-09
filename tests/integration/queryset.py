#!/usr/bin/env python
# coding=utf-8

"""Queryset integration tests."""

import copy
import json

import mongoengine_goodjson as gj
import mongoengine as db

from .schema import User, UserReferenceNoAutoSave
from .fixtures import users, users_dict
from ..connection_case import DBConBase


class UserSerializationDesrializationTest(DBConBase):
    """User serialization / deserialization integration test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None
        for user_el in copy.deepcopy(users):
            user_el.save()

    def test_encode(self):
        """The data should be encoded properly."""
        result = sorted(
            json.loads(User.objects.to_json()), key=lambda obj: obj["id"]
        )
        self.assertSequenceEqual(
            sorted(result, key=lambda obj: obj["id"]), users_dict
        )

    def test_decode(self):
        """The data should be decoded properly."""
        result = User.objects.from_json(json.dumps(users_dict))
        self.assertListEqual(users, result)


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
        self.users = copy.deepcopy(users)
        self.data_users = users_dict
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
