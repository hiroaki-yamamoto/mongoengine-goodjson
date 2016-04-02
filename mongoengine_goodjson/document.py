#!/usr/bin/env python
# coding=utf-8

"""Documents implementing human-readable JSON serializer."""

import json

import mongoengine as db
from .encoder import GoodJSONEncoder


class Document(db.Document):
    """Document implementing human-readable JSON serializer."""

    meta = {"abstract": True}

    def to_json(self, *args, **kwargs):
        """Encode to human-readable json."""
        use_db_field = kwargs.pop('use_db_field', True)
        if "cls" not in kwargs or len(args) < 5:
            kwargs["cls"] = GoodJSONEncoder
        data = self.to_mongo(use_db_field)
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id", None)
        return json.dumps(
            data, *args, **kwargs
        )


class EmbeddedDocument(db.EmbeddedDocument):
    """EmbeddedDocument implementing human-readable JSON serializer."""

    meta = {"abstract": True}

    def to_json(self, *args, **kwargs):
        """Encode to human-readable json."""
        use_db_field = kwargs.pop('use_db_field', True)
        if "cls" not in kwargs or len(args) < 5:
            kwargs["cls"] = GoodJSONEncoder
        data = self.to_mongo(use_db_field)
        return json.dumps(
            data, *args, **kwargs
        )
