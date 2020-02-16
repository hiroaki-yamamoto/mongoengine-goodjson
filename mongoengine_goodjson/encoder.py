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

from .utils import method_dispatch, id_first

from bson import (
    ObjectId, DBRef, RE_TYPE, Regex, MinKey, MaxKey, Timestamp, Code, Binary,
    PY3, SON
)
from bson.py3compat import text_type, string_type


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

    @method_dispatch
    def default(self, obj):
        """
        Convert the object into JSON-serializable value.

        Parameters:
            obj: Object to be converted.

        """
        super(GoodJSONEncoder, self).default(obj)

    @default.register(ObjectId)
    @default.register(UUID)
    def __conv_objid(self, obj):
        return text_type(obj)

    @default.register(datetime)
    def __conv_datetime(self, obj):
        if self.epoch_mode:
            return int(
                (timegm(obj.timetuple()) * 1000) +
                ((obj.microsecond) / 1000)
            )
        return obj.isoformat()

    @default.register(DBRef)
    def __conv_dbref(self, obj):
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
    def __conv_regex(self, obj):
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
    def __conv_minkey(self, obj):
        return {"minKey": True}

    @default.register(MaxKey)
    def __conv_maxkey(self, obj):
        return {"maxKey": True}

    @default.register(Timestamp)
    def __conv_timestamp(self, obj):
        return {"time": obj.time, "inc": obj.inc}

    @default.register(Code)
    def __conv_code(self, obj):
        return {"code": str(obj), "scope": obj.scope}

    @default.register(SON)
    def _conv_son(self, obj):
        return obj.to_dict()

    @default.register(Binary)
    def __conv_bin(self, obj):
        return {
            "data": b64encode(obj).decode("utf-8"),
            "type": obj.subtype
        }

    if PY3:
        @default.register(bytes)
        def __conv_bytes(self, obj):
            return {"data": b64encode(obj).decode("utf-8"), "type": 0}

    @method_dispatch
    def __check(self, obj):
        return obj

    @__check.register(Binary)
    def __conv_type(self, obj):
        return self.default(obj)

    @method_dispatch
    def encode(self, o, **kwargs):
        """encode."""
        return super(GoodJSONEncoder, self).encode(o, **kwargs)
    encode.register(text_type)(encode.dispatch(str))
    encode.register(string_type)(encode.dispatch(str))

    @encode.register(dict)
    def __encode_dict(self, o, **kwargs):
        return super(GoodJSONEncoder, self).encode(id_first({
            key: self.__check(value) for (key, value) in o.items()
        }), **kwargs)

    @encode.register(collections.Iterable)
    def __encode_list(self, o, **kwargs):
        return super(GoodJSONEncoder, self).encode([
            self.__check(value) for value in o
        ], **kwargs)
