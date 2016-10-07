#!/usr/bin/env python
# coding=utf-8

"""Follow Refernce Field Test."""

from ...connection_case import DBConBase as TestCase

from bson import ObjectId
import mongoengine as db
import mongoengine_goodjson as gj


class FollowreferenceFieldTestBase(TestCase):
    """Test basis class."""

    def setUp(self):
        """Setup."""
        self.maxDiff = None

        class User(gj.Document):
            name = db.StringField()
            email = db.EmailField()

        class TestDocument(gj.Document):
            value = db.StringField()
            author = gj.FollowReferenceField(User)
            contributors = db.ListField(gj.FollowReferenceField(User))

        self.user_model_cls = User
        self.test_model_cls = TestDocument
        self.users_data = [
            {
                "id": ObjectId(),
                "name": ("Test Example {}").format(counter),
                "email": ("test{}@example.com").format(counter)
            } for counter in range(3)
        ]
        self.tests_data = [
            {
                "id": ObjectId(),
                "value": ("test{}").format(counter),
                "author": self.users_data[counter]["id"],
                "contributors": [
                    user["id"] for (index, user) in enumerate(self.users_data)
                    if index != counter
                ]
            } for counter in range(3)
        ]

    def tearDown(self):
        """Teardown."""
        self.user_model_cls.drop_collection()
        self.test_model_cls.drop_collection()


class FollowReferenceFieldLoadTest(FollowreferenceFieldTestBase):
    """Follow Reference Field Load Test."""

    def setUp(self):
        """Setup."""
        super(FollowReferenceFieldLoadTest, self).setUp()
        for user_data in self.users_data:
            self.user_model_cls(**user_data).save()
        for test_data in self.tests_data:
            self.test_model_cls(**test_data).save()

    def test_user_model_load(self):
        """User model should be loaded."""
        users_data = sorted(
            self.user_model_cls.objects().as_pymongo(),
            key=lambda obj: obj["_id"]
        )
        for user_data in users_data:
            user_data["id"] = user_data.pop("_id")
        self.assertSequenceEqual(
            users_data, sorted(self.users_data, key=lambda obj: obj["id"])
        )

    def test_model_load(self):
        """Test model should be loaded."""
        tests_data = list(self.test_model_cls.objects().as_pymongo())
        for test_data in tests_data:
            test_data["id"] = test_data.pop("_id")
        self.assertListEqual(tests_data, self.tests_data)
