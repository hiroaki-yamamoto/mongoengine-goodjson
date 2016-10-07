#!/usr/bin/env python

"""Schema samples for integration tests."""

import mongoengine as db
from mongoengine_goodjson import (
    Document, EmbeddedDocument, FollowReferenceField
)


class Address(EmbeddedDocument):
    """Test schema."""

    street = db.StringField()
    city = db.StringField()
    state = db.StringField()


class User(Document):
    """Test schema."""

    name = db.StringField()
    email = db.EmailField()
    address = db.EmbeddedDocumentListField(Address)


class UserReferenceNoAutoSave(Document):
    """Test schema."""

    ref = FollowReferenceField(User)
    refs = db.ListField(FollowReferenceField(User))


class UserReferenceDisabledIDCheck(Document):
    """Test schema."""

    ref = FollowReferenceField(User, id_check=False)
    refs = db.ListField(FollowReferenceField(User, id_check=False))


class UserReferenceAutoSave(Document):
    """Test schema."""

    ref = FollowReferenceField(User, autosave=True)
    refs = db.ListField(FollowReferenceField(User, autosave=True))


class Email(Document):
    """Test schema."""

    email = db.EmailField(primary_key=True)


class Seller(EmbeddedDocument):
    """Test schema."""

    name = db.StringField()
    address = db.EmbeddedDocumentField(Address)


class ArticleMetaData(EmbeddedDocument):
    """Test schema."""

    price = db.IntField()
    seller = db.EmbeddedDocumentField(Seller)


class Article(Document):
    """Test schema."""

    user = db.ReferenceField(User)
    addition = db.EmbeddedDocumentField(ArticleMetaData)
    title = db.StringField()
    date = db.DateTimeField()
    body = db.BinaryField()
    uuid = db.UUIDField()


class Reference(Document):
    """Test schema."""

    name = db.StringField()
    references = db.ListField(db.ReferenceField(Article))
