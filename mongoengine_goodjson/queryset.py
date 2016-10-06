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

    def as_pymongo(self, *args, **kwargs):
        """Return pymongo encoded dict."""
        from mongoengine_goodjson.fields import FollowReferenceField
        lst = super(QuerySet, self).as_pymongo()
        if getattr(self, "$$good_json$$", None):
            for item in lst:
                for (name, fld) in self._document._fields.items():
                    if isinstance(fld, FollowReferenceField):
                        item[name] = fld.document_type.objects(
                            id=item[name]
                        ).as_pymongo()[0]
                        if "id" not in item[name] and "_id" in item[name]:
                            item[name]["id"] = item[name].pop("_id")
        return lst

    def to_json(self, *args, **kwargs):
        """Convert to JSON."""
        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder
        setattr(self, "$$good_json$$", True)
        lst = self.as_pymongo()
        delattr(self, "$$good_json$$")
        # Using for loop twice is not good in the case that there's a lot of
        # data, and to reduce for loop, picking out the field of which exclude
        # fields are truhty is the idea
        # (If you know more suitable idea, make a PR.).
        exclude = [
            name for (name, fld) in self._document._fields.items() if any([
                getattr(fld, "exclude_to_json", None),
                getattr(fld, "exclude_json", None)
            ])
        ]
        for dct in lst:
            dct["id"] = dct.pop("_id", None)
            for exc in exclude:
                dct.pop(exc, None)
        return json.dumps(lst, *args, **kwargs)

    def from_json(self, json_data):
        """Convert from JSON."""
        mongo_data = json.loads(
            json_data, object_hook=generate_object_hook(self._document)
        )
        exclude = [
            name for (name, fld) in self._document._fields.items() if any([
                getattr(fld, "exclude_from_json", None),
                getattr(fld, "exclude_json", None)
            ])
        ]
        for item in mongo_data:
            for exc in exclude:
                item.pop(exc, None)
        return [
            self._document._from_son(bson.SON(data)) for data in mongo_data
        ]
