#!/usr/bin/env python
# coding=utf-8

import json
from datetime import datetime
from time import mktime

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

from bson import ObjectId, DBRef


class GoodJSONEncoder(json.JSONEncoder):
    """JSON Encoder for human and MongoEngine."""
    def __init__(self):
        """Initialize the object."""
        super(GoodJSONEncoder, self).__init__()

    def default(self, obj):
        """
        Convert the object into JSON-serializable value.

        Parameters:
            obj: Object to be converted.
        """
        @singledispatch
        def default(obj):
            super(GoodJSONEncoder, self).default(obj)

        @default.register(ObjectId)
        def objid(obj):
            return str(obj)

        @default.register(datetime)
        def conv_datetime(obj):
            return int(
                mktime(obj.timetuple())*1000 + obj.microsecond / 1000
            )

        @default.register(DBRef)
        def conv_dbref(obj):
            doc = obj.as_doc()
            ret = {
                "collection": doc["$ref"],
                "id": self.default(doc["$id"]),
                "db": doc["$db"]
            }
            ret.update({
                key: value
                for (key, value) in doc.items()
                if key[0] != "$"
            })
            return ret

        return default(obj)
