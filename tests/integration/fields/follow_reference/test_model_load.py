#!/usr/bin/env python
# coding=utf-8

"""Follow Refernce Field Test."""

from ....con_base import DBConBase as TestCase

from bson import ObjectId
import mongoengine as db
import mongoengine_goodjson as gj

from ...fixtures.base import Dictable


class FollowReferenceFieldLoadTest(TestCase):
    """Follow Reference Field Load Test."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None

        class User(Dictable, gj.Document):
            name = db.StringField()
            email = db.EmailField()

            @classmethod
            def generate_test_data(cls, count):
                ret = cls(
                    id=ObjectId(), name=("Test Example {}").format(count),
                    email=("test{}@example.com").format(count)
                )
                ret.save()
                return ret

        class TestDocument(Dictable, gj.Document):
            value = db.StringField()
            author = gj.FollowReferenceField(User)
            contributors = db.ListField(gj.FollowReferenceField(User))

            @classmethod
            def generate_test_data(cls, count, author, contributors):
                ret = cls(
                    id=ObjectId(), value=("test{}").format(count),
                    author=author, contributors=contributors
                )
                ret.save()
                return ret

        self.user_model_cls = User
        self.test_model_cls = TestDocument
        self.users_data = [
            User.generate_test_data(counter) for counter in range(3)
        ]
        self.tests_data = [
            TestDocument.generate_test_data(
                counter, self.users_data[counter],
                [
                    user for user in self.users_data
                    if user != self.users_data[counter]
                ]
            ) for counter in range(3)
        ]

    def tearDown(self):
        """Teardown."""
        self.user_model_cls.drop_collection()
        self.test_model_cls.drop_collection()

    def test_user_model_load(self):
        """User model should be loaded."""
        users_data = sorted(
            self.user_model_cls.objects().as_pymongo(),
            key=lambda obj: obj["_id"]
        )
        for user_data in users_data:
            user_data["id"] = user_data.pop("_id")
        self.assertEqual(
            users_data, sorted(
                [user.to_dict(oid_as_str=False) for user in self.users_data],
                key=lambda obj: obj["id"]
            )
        )

    def test_model_load(self):
        """Test model should be loaded."""
        tests_data = list(self.test_model_cls.objects().as_pymongo())
        for test_data in tests_data:
            test_data["id"] = test_data.pop("_id")
        self.assertEqual(
            tests_data,
            [
                data.to_dict(oid_as_str=False, call_child_to_dict=False)
                for data in self.tests_data
            ]
        )
