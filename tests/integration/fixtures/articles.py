#!/usr/bin/env python
# coding=utf-8

"""Article fixtures."""

from datetime import datetime, timedelta
from uuid import uuid5, NAMESPACE_DNS

from bson import ObjectId, Binary

import mongoengine as db
import mongoengine_goodjson as gj

from .base import Dictable
from .user import Address, User

now = datetime.utcnow()


class Seller(Dictable, gj.EmbeddedDocument):
    """Test schema."""

    name = db.StringField()
    address = db.EmbeddedDocumentField(Address)

    @classmethod
    def generate_test_data(cls, additional_suffix=""):
        """Generate test data."""
        ret = cls(
            name=("Test example{}").format(
                (" {}").format(additional_suffix) if additional_suffix else
                ""
            )
        )
        ret.address = Address.generate_test_data(ret)
        return ret


class ArticleMetaData(Dictable, gj.EmbeddedDocument):
    """Test schema."""

    price = db.IntField()
    seller = db.EmbeddedDocumentField(Seller)

    @classmethod
    def generate_test_data(cls, additional_suffix=""):
        """Generate test data."""
        return cls(
            seller=Seller.generate_test_data(additional_suffix),
            price=1000000
        )


class Article(Dictable, gj.Document):
    """Test schema."""

    user = db.ReferenceField(User)
    addition = db.EmbeddedDocumentField(ArticleMetaData)
    title = db.StringField()
    date = db.DateTimeField()
    body = db.BinaryField()
    uuid = db.UUIDField()

    @classmethod
    def generate_test_data(cls, user=None, additional_suffix=""):
        """Generate test data."""
        return cls(
            pk=ObjectId(),
            user=user or User.generate_test_data(additional_suffix),
            title=("Test Tile{}").format(
                (" {}").format(additional_suffix) if additional_suffix else ""
            ),
            date=now - timedelta(microseconds=now.microsecond % 1000),
            body=Binary(b"\x00\x01\x02\x03\x04"),
            uuid=uuid5(NAMESPACE_DNS, "This is a test"),
            addition=ArticleMetaData.generate_test_data(additional_suffix)
        )
