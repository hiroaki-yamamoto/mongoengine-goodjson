#!/usr/bin/env python
# coding=utf-8

"""Fixtures for integration tests."""

from bson import ObjectId

import mongoengine as db
import mongoengine_goodjson as gj

from .articles import Article
from .base import Dictable
from .user import User


class ExtraInformation(Dictable, db.EmbeddedDocument):
    """Extra information."""

    txt = db.StringField()

    @classmethod
    def generate_test_data(cls, additional_suffix=""):
        """Generate test data."""
        return cls(
            txt=("This is a test{}").format(
                (" {}").format(additional_suffix) if additional_suffix else
                ""
            )
        )


class ExtraReference(Dictable, gj.Document):
    """Extra reference info."""

    ref_txt = db.StringField()

    @classmethod
    def generate_test_data(cls, additional_suffix=""):
        """Generate test data."""
        return cls(
            pk=ObjectId(),
            ref_txt=("Reference test{}").format(
                (" {}").format(additional_suffix) if additional_suffix else
                ""
            )
        )


class Reference(Dictable, gj.Document):
    """Test schema."""

    name = db.StringField()
    ex_info = db.EmbeddedDocumentField(ExtraInformation)
    ex_ref = db.ReferenceField(ExtraReference)
    ex_refs = db.ListField(db.ReferenceField(ExtraReference))
    ex_dict = db.DictField(db.ReferenceField(ExtraReference))
    references = db.ListField(db.ReferenceField(Article))
    dict_references = db.DictField(db.ReferenceField(Article))

    @classmethod
    def generate_test_data(cls, user=None, article=None, additional_suffix=""):
        """Generate test data."""
        return cls(
            pk=ObjectId(), name="test", references=[
                article or Article.generate_test_data(
                    user=user or User.generate_test_data(
                        additional_suffix=additional_suffix
                    ),
                    additional_suffix=additional_suffix
                )
            ],
            dict_references={
                "test {}".format(ct): Article.generate_test_data(
                    user=user or User.generate_test_data(
                        additional_suffix="user_{}".format(additional_suffix)
                    ),
                    additional_suffix="dctt_test_{}".format(additional_suffix)
                ) for ct in range(3)
            },
            ex_info=ExtraInformation.generate_test_data(additional_suffix),
            ex_ref=ExtraReference.generate_test_data(additional_suffix),
            ex_refs=[
                ExtraReference.generate_test_data(
                    additional_suffix=("{}{}").format(additional_suffix, ct)
                )
                for ct in range(3)
            ],
            ex_dict={
                "test_{}".format(ct): ExtraReference.generate_test_data(
                    additional_suffix=("dct_{}{}").format(
                        additional_suffix, ct
                    )
                ) for ct in range(3)
            }
        )
