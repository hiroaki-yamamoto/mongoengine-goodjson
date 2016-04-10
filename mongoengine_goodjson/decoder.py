#!/usr/bin/env python
# coding=utf-8

"""Human-readable JSON decoder for MongoEngine."""

from base64 import b64decode
from datetime import datetime, timedelta
from uuid import UUID

import bson
from dateutil.parser import parse
import mongoengine as db
from mongoengine.base import BaseField

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch


def generate_object_hook(cls):
    """Human readable JSON decoder for MongoEngine."""
    fields = {} if cls is None else {
        field_name: field_type
        for (field_name, field_type) in cls.__dict__.items()
        if isinstance(field_type, BaseField)
    }

    def object_hook(dct):
        @singledispatch
        def decode(field_type, field_name, obj):
            return {field_name: field_type.to_python(obj)}

        @decode.register(db.ReferenceField)
        def deocde_reference(field_type, field_name, obj):
            return {
                field_name: field_type.to_python(
                    bson.DBRef(
                        obj["collection"], bson.ObjectId(obj["id"]),
                        database=obj.get("database")
                    ) if field_type.dbref else obj
                )
            }

        @decode.register(db.DateTimeField)
        def decode_datetime(fldtype, name, obj):

            @singledispatch
            def parse_datetime(obj):
                raise TypeError(
                    ("This type ({}) is not supported").format(
                        type(obj).__name__
                    )
                )

            @parse_datetime.register(int)
            def parse_int(obj):
                result = datetime.utcfromtimestamp(
                    int(obj / 1000)
                ) + timedelta(milliseconds=int(obj % 1000))
                return {name: result}

            @parse_datetime.register(str)
            def parse_str(obj):
                result = parse(obj)
                return {name: result}

            try:
                parse_datetime.register(unicode)(parse_str)  # noqa
            except NameError:
                pass

            return parse_datetime(obj)

        @decode.register(db.BinaryField)
        def decode_binary(fldtype, name, obj):
            return {
                name: bson.Binary(
                    b64decode(obj["data"]), subtype=obj["type"]
                )
            }

        @decode.register(db.UUIDField)
        def decode_uuid(fldtype, name, obj):
            return {name: UUID(obj)}

        if set(dct.keys()).issubset(set(fields.keys())):
            for (name, fldtype) in fields.items():
                value = dct.get(name)
                if value:
                    dct.update(decode(fldtype, name, value))
        return dct
    return object_hook
