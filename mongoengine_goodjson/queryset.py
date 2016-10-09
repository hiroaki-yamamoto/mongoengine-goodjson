#!/usr/bin/env python
# coding=utf-8

"""Queryset encoder."""

import json

try:
    from functools import singledispatch
except:
    from singledispatch import singledispatch

import bson
import mongoengine as db

from .encoder import GoodJSONEncoder
from .decoder import generate_object_hook


class QuerySet(db.QuerySet):
    """QuerySet that supports human-readable json."""

    def __start_good_json(self):
        """Start good json flag."""
        setattr(self, "$$good_json$$", True)

    def __end_good_json(self):
        """End good json flag."""
        setattr(self, "$$good_json$$", None)
        delattr(self, "$$good_json$$")

    def __get_doc(self, fld, item):
        """Get document as dict or a list of documents."""
        from mongoengine_goodjson.fields import FollowReferenceField

        @singledispatch
        def doc(fld, item):
            return item

        @doc.register(db.ListField)
        def doc_list(fld, item):
            return [self.__get_doc(fld.field, el) for el in item]

        @doc.register(FollowReferenceField)
        def doc_frl(fld, item):
            doc = fld.document_type.objects(id=item).get()
            doc.begin_goodjson()
            result = doc.to_mongo()
            doc.end_goodjson()
            return result

        result = doc(fld, item)

        if isinstance(result, dict) and "id" not in result and "_id" in result:
            result["id"] = result.pop("_id")
        return result

    def as_pymongo(self, *args, **kwargs):
        """Return pymongo encoded dict."""
        lst = super(QuerySet, self).as_pymongo()
        if getattr(self, "$$good_json$$", None):
            for item in lst:
                for (name, fld) in self._document._fields.items():
                    if name == "id":
                        name = "_id"
                    item[name] = self.__get_doc(fld, item[name])
                if "id" not in item and "_id" in item:
                    item["id"] = item.pop("_id")
        return lst

    def to_json(self, *args, **kwargs):
        """Convert to JSON."""
        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder
        self.__start_good_json()
        lst = self.as_pymongo()
        self.__end_good_json()
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
