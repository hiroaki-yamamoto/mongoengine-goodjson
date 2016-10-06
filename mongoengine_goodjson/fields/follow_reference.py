#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field code."""

import json
import mongoengine as db
from ..document import Document


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
            id_check: Set False to disable id check. By default, this value is
                True
            autosave: Set True to save/update the referenced document when
                to_python is called.
        """
        self.id_check = kwargs.pop("id_check", True)
        self.autosave = kwargs.pop("autosave", False)
        super(FollowReferenceField, self).__init__(*args, **kwargs)

    def to_mongo(self, document, **kwargs):
        """
        Convert to python-typed dict.

        Parameters:
            document: The document.
        """
        if not getattr(self, "$$good_json$$", None):
            return super(FollowReferenceField, self).to_mongo(
                document, **kwargs
            )
        ret = document
        if isinstance(document, db.Document):
            if document.pk is None and self.id_check:
                self.error("The referenced document needs ID.")
        else:
            ret = self.document_type.objects(
                pk=super(
                    FollowReferenceField, self
                ).to_mongo(document, **kwargs)
            ).get()
        ret = ret.to_mongo(**kwargs)
        if "_id" in ret and issubclass(self.document_type, Document):
            ret["id"] = ret.pop("_id", None)
        return ret

    def to_python(self, value):
        """
        Convert to python-based object.

        Parameters:
            value: The python-typed document.
        """
        clone = value
        if isinstance(value, dict):
            clone = self.document_type.from_json(
                json.dumps(value), created="id" not in value
            )
            if self.autosave:
                clone.save()
        ret = super(FollowReferenceField, self).to_python(clone)
        return ret
