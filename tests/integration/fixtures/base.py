#!/usr/bin/env python
# coding=utf-8

"""Base classes."""

from base64 import b64encode
from datetime import date
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch  # noqa
from uuid import UUID
from bson import ObjectId, Binary
from six import text_type


class Dictable(object):
    """To indicate the class can be converted into dict, inherit this."""

    def to_dict(self):
        """Convert the model into dict without to_mongo or to_json."""
        @singledispatch
        def to_primitive(value):
            # Convert value into primitive type.
            return value

        @to_primitive.register(Dictable)
        def value_dict(value):
            return value.to_dict()

        @to_primitive.register(date)
        def value_date_datetime(value):
            return value.isoformat()

        @to_primitive.register(ObjectId)
        @to_primitive.register(UUID)
        def value_needs_stringify(value):
            return text_type(value)

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
            for key in self._fields.keys()
        }
