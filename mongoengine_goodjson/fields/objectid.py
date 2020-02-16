#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-defined Object ID Field."""

import typing
import bson.objectid as oid
from mongoengine.base.fields import ObjectIdField


class ObjectIDField(ObjectIdField):
    """Revised Object ID Field."""

    def to_mongo(self, value: typing.Any, to_json=False):
        """Convert into Python ObjectID."""
        ret = value
        if not isinstance(value, oid.ObjectId):
            try:
                ret = oid.ObjectId(str(value))
            except Exception as e:
                self.error(str(e))
        if to_json:
            ret = str(ret)
        return ret
