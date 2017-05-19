#!/usr/bin/env python
# coding=utf-8

"""Base classes."""

from base64 import b64encode
from datetime import date
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch  # noqa
from mongoengine import Document, EmbeddedDocument
from uuid import UUID
from bson import ObjectId, Binary
from six import text_type


class Dictable(object):
    """To indicate the class can be converted into dict, inherit this."""

    def to_dict(
        self, oid_as_str=True, call_child_to_dict=True,
        cur_depth=0, max_depth=3
    ):
        """
        Convert the model into dict without to_mongo or to_json.

        Parameters:
            oid_as_str: Set False if you **dont't** want to convert ObjectId
                into str.
            call_child_to_dict: Set False to skip calling to_dict of child
                doc.

        """
        @singledispatch
        def to_primitive(value):
            # Convert value into primitive type.
            return value

        if call_child_to_dict and cur_depth < max_depth:
            @to_primitive.register(Dictable)
            def value_dict(value):
                return value.to_dict(
                    call_child_to_dict=call_child_to_dict,
                    oid_as_str=oid_as_str,
                    cur_depth=(
                        cur_depth if isinstance(value, EmbeddedDocument)
                        else cur_depth + 1
                    )
                )
        else:
            @to_primitive.register(Document)
            def return_reference_id(value):
                return to_primitive(value.id)

            @to_primitive.register(EmbeddedDocument)
            def return_emb_doc(value):
                return value.to_dict(
                    oid_as_str=oid_as_str,
                    call_child_to_dict=call_child_to_dict,
                    cur_depth=cur_depth, max_depth=max_depth
                ) if hasattr(value, "to_dict") else value.to_mongo()

        @to_primitive.register(date)
        def value_date_datetime(value):
            return value.isoformat()

        @to_primitive.register(UUID)
        def value_needs_stringify(value):
            return text_type(value)

        if oid_as_str:
            to_primitive.register(ObjectId)(value_needs_stringify)

        @to_primitive.register(Binary)
        def value_binary(value):
            return {
                text_type("data"): text_type(b64encode(value).decode("utf-8")),
                text_type("type"): value.subtype
            }

        @to_primitive.register(list)
        def value_list(value):
            return [to_primitive(item) for item in value]

        return {
            key: to_primitive(getattr(self, key))
            for key in self._fields.keys() if getattr(self, key) is not None
        }
