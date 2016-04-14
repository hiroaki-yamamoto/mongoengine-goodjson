#!/usr/bin/env python
# coding=utf-8

"""Encoder module."""

import collections
import json
import re
from base64 import b64encode
from datetime import datetime
from calendar import timegm
from uuid import UUID

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

from bson import (
    ObjectId, DBRef, RE_TYPE, Regex, MinKey, MaxKey, Timestamp, Code, Binary,
    PY3
)
from bson.py3compat import text_type


class GoodJSONEncoder(json.JSONEncoder):
    """JSON Encoder for human and MongoEngine."""

    def __init__(self, epoch_mode=False, *args, **kwargs):
        """
        Initialize the object.

        Parameters:
            epoch_mode: Set True if you want to serialize datetime into epoch
                millisecond. By default, this parameter is set to False, which
                means the serializer serializes datetime into ISO-formatted
                string.
        """
        self.epoch_mode = epoch_mode
        super(GoodJSONEncoder, self).__init__(*args, **kwargs)

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
        @default.register(UUID)
        def conv_objid(obj):
            return text_type(obj)

        @default.register(datetime)
        def conv_datetime(obj):
            if self.epoch_mode:
                return int(
                    (timegm(obj.timetuple()) * 1000) +
                    ((obj.microsecond) / 1000)
                )
            return obj.isoformat()

        @default.register(DBRef)
        def conv_dbref(obj):
            doc = obj.as_doc()
            ret = {
                "collection": doc["$ref"],
                "id": self.default(doc["$id"])
            }
            if obj.database:
                ret["db"] = doc["$db"]
            ret.update({
                key: value
                for (key, value) in doc.items()
                if key[0] != "$"
            })
            return ret

        @default.register(RE_TYPE)
        @default.register(Regex)
        def conv_regex(obj):
            flags_map = {
                "i": obj.flags & re.IGNORECASE,
                "l": obj.flags & re.LOCALE,
                "m": obj.flags & re.MULTILINE,
                "s": obj.flags & re.DOTALL,
                "u": obj.flags & re.UNICODE,
                "x": obj.flags & re.VERBOSE
            }
            flags = [key for (key, contains) in flags_map.items() if contains]
            ret = {"regex": obj.pattern}
            if flags:
                ret["flags"] = ("").join(flags)
            return ret

        @default.register(MinKey)
        def conv_minkey(obj):
            return {"minKey": True}

        @default.register(MaxKey)
        def conv_maxkey(obj):
            return {"maxKey": True}

        @default.register(Timestamp)
        def conv_timestamp(obj):
            return {"time": obj.time, "inc": obj.inc}

        @default.register(Code)
        def conv_code(obj):
            return {"code": str(obj), "scope": obj.scope}

        @default.register(Binary)
        def conv_bin(obj):
            return {
                "data": b64encode(obj).decode("utf-8"),
                "type": obj.subtype
            }

        if PY3:
            @default.register(bytes)
            def conv_bytes(obj):
                return {"data": b64encode(obj).decode("utf-8"), "type": 0}

        return default(obj)

    def encode(self, o, **kwargs):
        """encode."""
        # I appologize that I wrote this bad code.
        # The reason why I wrote this code is because Binary class inherits
        # bytes. bytes is the same of str in python2, but byte is treated as
        # "binary" type in python3. If I can lock into python3, this encode
        # function is not needed. However, this code is used on the both
        # of python3 and python2. Therefore, needs to convert Binary
        # instance into the corresponding dict first...
        #
        # In addition, I think there are other types that have compatibility
        # problem like above. (Of course, pull request is appreciated)
        @singledispatch
        def check(obj):
            return obj

        @check.register(Binary)
        def conv_type(obj):
            return self.default(obj)

        ret = {
            key: check(value) for (key, value) in o.items()
        } if isinstance(o, dict) else [
            check(value) for value in o
        ] if not isinstance(o, str) and \
            isinstance(o, collections.Iterable) else o
        return super(GoodJSONEncoder, self).encode(ret, **kwargs)
