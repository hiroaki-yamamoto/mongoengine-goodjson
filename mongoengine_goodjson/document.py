#!/usr/bin/env python
# coding=utf-8

"""Documents implementing human-readable JSON serializer."""

import json

import mongoengine as db
from bson import SON
from .encoder import GoodJSONEncoder
from .decoder import generate_object_hook
from .queryset import QuerySet


class Helper(object):
    """Helper class to serialize / deserialize JSON document."""

    def to_json(self, *args, **kwargs):
        """Encode to human-readable json."""
        use_db_field = kwargs.pop('use_db_field', True)
        data = self.to_mongo(use_db_field)
        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id", None)
        return json.dumps(data, *args, **kwargs)

    @classmethod
    def from_json(cls, json_str, *args, **kwargs):
        """Decode from human-readable json."""
        hook = generate_object_hook(cls)
        if "object_hook" not in kwargs:
            kwargs["object_hook"] = hook
        dct = json.loads(json_str, *args, **kwargs)
        return cls._from_son(SON(dct))


class Document(Helper, db.Document):
    """Document implementing human-readable JSON serializer."""

    meta = {
        "abstract": True,
        "queryset_class": QuerySet
    }


class EmbeddedDocument(Helper, db.EmbeddedDocument):
    """EmbeddedDocument implementing human-readable JSON serializer."""

    meta = {
        "abstract": True,
        "queryset_class": QuerySet
    }
