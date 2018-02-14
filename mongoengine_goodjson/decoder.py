#!/usr/bin/env python
# coding=utf-8

"""Human-readable JSON decoder for MongoEngine."""

from base64 import b64decode
from datetime import datetime, timedelta
from uuid import UUID

import bson
from dateutil.parser import parse
import mongoengine as db

from .utils import method_dispatch


class ObjectHook(object):
    """
    Human readable JSON decoder for MongoEngine.

    Note the instance of this object is callable object, so you can create
    the instance of this class, then, put object_hook kwargs.

    """

    def __init__(self, cls):
        """
        Initialize the object.

        cls is the class type of Document. Note that this is not the instance,
        just the definition of the document.
        """
        self.cls = cls

    @method_dispatch
    def __parse_datetime(self, obj, name):
        raise TypeError(
            ("This type ({}) is not supported").format(
                type(obj).__name__
            )
        )

    @__parse_datetime.register(int)
    def __parse_date_from_int(self, obj, name):
        result = datetime.utcfromtimestamp(
            int(obj / 1000)
        ) + timedelta(milliseconds=int(obj % 1000))
        return {name: result}

    @__parse_datetime.register(bson.py3compat.string_type)
    @__parse_datetime.register(bson.py3compat.text_type)
    def __parse_date_from_str(self, obj, name):
        result = parse(obj)
        return {name: result}

    @method_dispatch
    def __decode(self, field_type, field_name, obj):
        return {field_name: field_type.to_python(obj)}

    @__decode.register(db.ReferenceField)
    def __deocde_reference(self, field_type, field_name, obj):
        return {
            field_name: field_type.to_python(
                bson.DBRef(
                    obj["collection"], bson.ObjectId(obj["id"]),
                    database=obj.get("database")
                ) if field_type.dbref else obj
            )
        }

    @__decode.register(db.DateTimeField)
    def __decode_datetime(self, fldtype, name, obj):
        return self.__parse_datetime(obj, name)

    @__decode.register(db.BinaryField)
    def __decode_binary(self, fldtype, name, obj):
        return {
            name: bson.Binary(
                b64decode(obj["data"]), subtype=obj["type"]
            )
        }

    @__decode.register(db.UUIDField)
    def __decode_uuid(self, fldtype, name, obj):
        return {name: UUID(obj)}

    def __call__(self, dct):
        """Call object hook."""
        fields = {} if self.cls is None else self.cls._fields
        if set(dct.keys()).issubset(set(fields.keys())):
            for (name, fldtype) in fields.items():
                value = dct.get(name)
                if value:
                    dct.update(self.__decode(fldtype, name, value))
        return dct


generate_object_hook = ObjectHook
