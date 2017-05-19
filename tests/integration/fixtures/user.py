#!/usr/bin/env python
# coding=utf-8

"""User fixture."""

from bson import ObjectId

import mongoengine as db
import mongoengine_goodjson as gj

from .base import Dictable


class Address(Dictable, gj.EmbeddedDocument):
    """Test schema."""

    street = db.StringField()
    city = db.StringField()
    state = db.StringField()

    @classmethod
    def generate_test_data(cls, user, additional_suffix=""):
        """Generate test data."""
        return cls(
            street=("Test street {} {}").format(user.name, additional_suffix),
            city=("Test city {} {}").format(user.name, additional_suffix),
            state=("Test state {} {}").format(user.name, additional_suffix)
        )


class User(Dictable, gj.Document):
    """Test schema."""

    name = db.StringField()
    email = db.EmailField()
    address = db.EmbeddedDocumentListField(Address)
    metadata = db.DictField()

    @classmethod
    def generate_test_data(cls, additional_suffix=""):
        """Generate test data."""
        user = cls(
            id=ObjectId(),
            name=("Test man{}").format(
                (" {}").format(additional_suffix) if additional_suffix else ""
            ),
            email=("test{}@example.com").format(additional_suffix)
        )
        user.address = [
            Address.generate_test_data(user, additional_suffix=counter)
            for counter in range(3)
        ]
        user.metadata = {
            ("test{}").format(counter1): {
                ("test2_{}").format(counter2):
                    ("Test value {}").format(counter2)
                for counter2 in range(3)
            }
            for counter1 in range(5)
        }
        return user


class UserReferenceNoAutoSave(Dictable, gj.Document):
    """Test schema."""

    ref = gj.fields.FollowReferenceField(User)
    refs = db.ListField(gj.fields.FollowReferenceField(User))


class UserReferenceDisabledIDCheck(Dictable, gj.Document):
    """Test schema."""

    ref = gj.fields.FollowReferenceField(User, id_check=False)
    refs = db.ListField(gj.fields.FollowReferenceField(User, id_check=False))


class UserReferenceAutoSave(Dictable, gj.Document):
    """Test schema."""

    ref = gj.fields.FollowReferenceField(User, autosave=True)
    refs = db.ListField(gj.fields.FollowReferenceField(User, autosave=True))
