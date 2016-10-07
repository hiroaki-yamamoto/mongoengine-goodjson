#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field Test schema."""

import mongoengine as db

import mongoengine_goodjson as gj
import mongoengine_goodjson.document as gj_doc
import six


class Helper(object):
    """Helper class."""

    begin_goodjson = six.get_unbound_function(gj_doc.Helper.begin_goodjson)
    __set_gj_flag_sub_field = six.get_unbound_function(
        gj_doc.Helper.__set_gj_flag_sub_field
    )
    __unset_gj_flag_sub_field = six.get_unbound_function(
        gj_doc.Helper.__unset_gj_flag_sub_field
    )


class ReferencedDocument(db.Document):
    """Referenced document."""

    name = db.StringField()


class IDCheckDocument(Helper, db.Document):
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


class DisabledIDCheckDocument(Helper, db.Document):
    """Test document disabling id check."""

    ref = gj.FollowReferenceField(ReferencedDocument, id_check=False)

    def __init__(self, enable_gj=False, *args, **kwargs):
        """Init the class."""
        super(DisabledIDCheckDocument, self).__init__(*args, **kwargs)
        if enable_gj:
            self.begin_goodjson()
