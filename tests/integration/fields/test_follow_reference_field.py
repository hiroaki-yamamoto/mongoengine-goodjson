#!/usr/bin/env python
# coding=utf-8

"""Follow Refernce Field Test."""

from unittest import TestCase

from bson import ObjectId
import mongoengine as db
import mongoengine_goodjson as gj


class FollowreferenceFieldTestBase(TestCase):
    """Test basis class."""

    @classmethod
    def setUpClass(cls):
        """Setup class."""
        cls.maxDiff = None

        class User(gj.Document):
            name = db.StringField()
            email = db.EmailField()

        class TestDocument(gj.Document):
            value = db.StringField()
            author = gj.FollowReferenceField(User)
            contributors = db.ListField(gj.FollowReferenceField(User))

        cls.user_model_cls = User
        cls.test_model_cls = TestDocument
        cls.users_data = [
            {
                "id": ObjectId(),
                "name": ("Test Example {}").format(counter),
                "email": ("test{}@example.com").format(counter)
            } for counter in range(3)
        ]
        cls.tests_data = [
            {
                "id": ObjectId(),
                "value": ("test{}").format(counter),
                "author": cls.users_data[counter]["id"],
                "contributors": [
                    user["id"] for (index, user) in enumerate(cls.users_data)
                    if index != counter
                ]
            } for counter in range(3)
        ]

    @classmethod
    def tearDownClass(cls):
        """Tear down class."""
        cls.user_model_cls.drop_collection()
        cls.test_model_cls.drop_collection()


class FollowReferenceFieldLoadTest(FollowreferenceFieldTestBase):
    """Follow Reference Field Load Test."""

    @classmethod
    def setUpClass(cls):
        """Setup."""
        super(FollowReferenceFieldLoadTest, cls).setUpClass()
        for user_data in cls.users_data:
            cls.user_model_cls(**user_data).save()
        for test_data in cls.tests_data:
            cls.test_model_cls(**test_data).save()

    def test_user_model_load(self):
        """User model should be loaded."""
        users_data = list(self.user_model_cls.objects().as_pymongo())
        for user_data in users_data:
            user_data["id"] = user_data.pop("_id")
        self.assertListEqual(users_data, self.users_data)

    def test_model_load(self):
        """Test model should be loaded."""
        tests_data = list(self.test_model_cls.objects().as_pymongo())
        for test_data in tests_data:
            test_data["id"] = test_data.pop("_id")
        self.assertListEqual(tests_data, self.tests_data)
