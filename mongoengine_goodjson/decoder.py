#!/usr/bin/env python
# coding=utf-8

"""Human-readable JSON decoder for MongoEngine."""

from mongoengine.base import BaseField


def generate_object_hook(cls):
    """Human readable JSON decoder for MongoEngine."""
    fields = {} if cls is None else {
        field_name: field_type
        for (field_name, field_type) in cls.__dict__.items()
        if isinstance(field_type, BaseField)
    }

    def object_hook(dct):
        for (field_name, field_type) in fields.items():
            if field_name in dct:
                return {field_name: field_type.to_python(dct[field_name])}
        return dct
    return object_hook
