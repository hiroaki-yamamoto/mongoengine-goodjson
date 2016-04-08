#!/usr/bin/env python

"""Schema samples for integration tests."""

import mongoengine as db
from mongoengine_goodjson import Document, EmbeddedDocument


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


class Relationship(Document):
    """Test schema."""

    name = db.StringField()
    relation = db.ListField(db.ReferenceField("self"))
    best = db.ReferenceField("self")
