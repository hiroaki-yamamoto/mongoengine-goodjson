#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Follow Reference Field."""

import typing

from bson import DBRef
from mongoengine.fields import ReferenceField

from mongoengine_goodjson.document import Document


class FollowReferenceField(ReferenceField):
    """Follow Reference Field."""

    def __init__(self, document_type, num_access=3, *args, **kwargs):
        """
        Initialize the field instance.

        Parameters:
            num_access: The number that to_mongo / to_json can access this
                field. When the number of the call exceeded this number,
                to_mongo method returns the object id as the standard
                MongoEngine field does. Note that this parameter can be a
                callable with source document as the first argument, target
                document as the second argument, and whether the reference
                should be continued (True), or not (False) as the return value.
                By default, the value is 3.
            *args, **kwargs: Any (keyword) arguments that
                should be passed to mongoengine.fields.ReferenceField.
        """
        kwargs.setdefault("num_access", 3)
        super().__init__(document_type, num_access=num_access, *args, **kwargs)

    def to_mongo(self, document: Document) -> typing.Dict[str, typing.Any]:
        """Serialize the reference into the document."""
        _id = super().to_mongo(document)
        return isinstance(_id, DBRef) and _id.as_doc() or document.as_doc()
