#!/usr/bin/env python
# coding=utf-8

import json
from datetime import datetime
from time import mktime

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

from bson import ObjectId


class GoodJSONEncoder(json.JSONEncoder):
    '''
    JSON Encoder for human and MongoEngine
    '''
    def __init__(self):
        super(GoodJSONEncoder, self).__init__()

    def default(self, obj):
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

        return default(obj)
