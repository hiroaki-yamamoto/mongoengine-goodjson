#!/usr/bin/env python
# coding=utf-8

"""Queryset encoder."""

import json

import bson
import mongoengine as db

from .encoder import GoodJSONEncoder
from .decoder import generate_object_hook


class QuerySet(db.QuerySet):
    """QuerySet that supports human-readable json."""

    def to_json(self, *args, **kwargs):
        """Convert to JSON."""
        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder
        lst = self.as_pymongo()
        for dct in lst:
            dct["id"] = dct.pop("_id", None)
        return json.dumps(lst, *args, **kwargs)

    def from_json(self, json_data):
        """Convert from JSON."""
        mongo_data = json.loads(
            json_data, object_hook=generate_object_hook(self._document)
        )
        return [
            self._document._from_son(bson.SON(data)) for data in mongo_data
        ]
