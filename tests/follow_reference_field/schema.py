#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field Test schema."""

import mongoengine as db

import mongoengine_goodjson as gj
import mongoengine_goodjson.document as gj_doc


class ReferencedDocument(db.Document):
    """Referenced document."""

    name = db.StringField()


class IDCheckDocument(gj_doc.Helper, db.Document):
    """
    Test document.

    By default, the id must be checked.
    """

    ref = gj.FollowReferenceField(ReferencedDocument)

    def __init__(self, enable_gj=False, *args, **kwargs):
        """Init the class."""
        super(IDCheckDocument, self).__init__(*args, **kwargs)
        if enable_gj:
            self.begin_goodjson()


class DisabledIDCheckDocument(gj_doc.Helper, db.Document):
    """Test document disabling id check."""

    ref = gj.FollowReferenceField(ReferencedDocument, id_check=False)

    def __init__(self, enable_gj=False, *args, **kwargs):
        """Init the class."""
        super(DisabledIDCheckDocument, self).__init__(*args, **kwargs)
        if enable_gj:
            self.begin_goodjson()
