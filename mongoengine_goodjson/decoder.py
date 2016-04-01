#!/usr/bin/env python
# coding=utf-8

"""Human-readable JSON decoder for MongoEngine."""

from datetime import datetime, timedelta

import bson
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
            return {field_name: field_type.to_python(dct[field_name])}

        @decode.register(db.ReferenceField)
        def deocde_reference(field_type, field_name, obj):
            if field_type.dbref:
                return {
                    field_name: bson.DBRef(
                        obj["collection"], bson.ObjectId(obj["id"]),
                        database=obj.get("database")
                    )
                }

        @decode.register(db.DateTimeField)
        def decode_datetime(fldtype, name, obj):
            result = datetime.utcfromtimestamp(
                int(obj / 1000)
            ) + timedelta(milliseconds=int(obj % 1000))
            return {name: result}

        if set(dct.keys()).issubset(set(fields.keys())) and \
                len(dct.keys()) < 2:
            name = list(dct.keys())[0]
            value = dct[name]
            fldtype = fields[name]
            return decode(fldtype, name, value)
        return dct
    return object_hook
