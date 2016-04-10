#!/usr/bin/env python

"""Schema samples for integration tests."""

import mongoengine as db
from mongoengine_goodjson import Document, EmbeddedDocument


class EqualityBase(object):
    """Equality base."""

    def __eq__(self, other):
        """Check equality."""
        return all([
            self[fldname] == other[fldname]
            for fldname in self
        ]) and len(other) == len(self)

    def __ne__(self, other):
        """Check inequality."""
        return not (self == other)


class EqualityDocumentBase(EqualityBase, Document):
    """Test schema."""

    meta = {"abstract": True}


class EqualityEmbeddedDocumentBase(EqualityBase, EmbeddedDocument):
    """Test schema."""

    meta = {"abstract": True}


class Address(EqualityEmbeddedDocumentBase):
    """Test schema."""

    street = db.StringField()
    city = db.StringField()
    state = db.StringField()


class User(EqualityDocumentBase):
    """Test schema."""

    name = db.StringField()
    email = db.EmailField()
    address = db.EmbeddedDocumentListField(Address)


class Email(EqualityDocumentBase):
    """Test schema."""

    email = db.EmailField(primary_key=True)


class Seller(EqualityEmbeddedDocumentBase):
    """Test schema."""

    name = db.StringField()
    address = db.EmbeddedDocumentField(Address)


class ArticleMetaData(EqualityEmbeddedDocumentBase):
    """Test schema."""

    price = db.IntField()
    seller = db.EmbeddedDocumentField(Seller)


class Article(EqualityDocumentBase):
    """Test schema."""

    user = db.ReferenceField(User)
    addition = db.EmbeddedDocumentField(ArticleMetaData)
    title = db.StringField()
    date = db.DateTimeField()
    body = db.BinaryField()
    uuid = db.UUIDField()


class Reference(EqualityDocumentBase):
    """Test schema."""

    name = db.StringField()
    references = db.ListField(db.ReferenceField(Article))
