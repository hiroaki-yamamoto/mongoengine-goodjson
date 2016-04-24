#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field Test schema."""

import mongoengine as db

import mongoengine_goodjson as gj


class ReferencedDocument(db.Document):
    """Referenced document."""

    name = db.StringField()


class IDCheckDocument(db.Document):
    """
    Test document.

    By default, the id must be checked.
    """

    ref = gj.FollowReferenceField(ReferencedDocument)


class DisabledIDCheckDocument(db.Document):
    """Test document disabling id check."""

    ref = gj.FollowReferenceField(ReferencedDocument, id_check=False)
