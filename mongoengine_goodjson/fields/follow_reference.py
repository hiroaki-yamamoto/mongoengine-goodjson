#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field code."""

import mongoengine as db


class FollowReferenceField(db.ReferenceField):
    """
    Follow Reference Field.

    This field can be treated as a field like ReferenceField, but generates
    the JSON/dict of the referenced document like embedded document.

    Note:
        This field doesn't check recursion level. Therefore, please be careful
        for self-referenced document.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class.

        Parameters:
            *args, **kwsrgs: Any arguments to be passed to ReferenceField.
        Keyword Arguments:
            id_check: Set false to disable id check. By default, this value is
                True
        """
        self.id_check = kwargs.pop("id_check", True)
        super(FollowReferenceField, self).__init__(*args, **kwargs)

    def to_mongo(self, document):
        """
        Convert to python-typed dict.

        Parameters:
            document: The document.
        """
        if document.pk is None and self.id_check:
            self.error("The referenced document needs ID.")
