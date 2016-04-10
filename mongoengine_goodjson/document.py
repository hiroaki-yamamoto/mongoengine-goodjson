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

    def _follow_reference(self, max_depth, current_depth,
                          use_db_field, *args, **kwargs):
        ret = {}
        for fldname in self:
            fld = self._fields.get(fldname)
            is_list = isinstance(fld, db.ListField)
            target = fld.field if is_list else fld

            if isinstance(target, db.ReferenceField):
                value = [
                    json.loads(
                        doc.to_json(
                            follow_reference=True,
                            max_depth=max_depth,
                            current_depth=current_depth + 1,
                            use_db_field=use_db_field,
                            *args, **kwargs
                        )
                    ) for doc in self[fldname]
                ] if is_list else json.loads(self[fldname].to_json(
                    follow_reference=True,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    use_db_field=use_db_field,
                    *args, **kwargs
                ))
                if value is not None:
                    ret.update({fldname: value})
        return ret

    def to_json(self, *args, **kwargs):
        """
        Encode to human-readable json.

        Parameters:
            use_db_field: use_db_field that is passed to to_mongo.
            follow_reference: set True to follow reference field.
            max_depth: maximum recursion depth. If this value is set to None,
                the reference is followed until it is end. Setting 0 is the
                same meaning of follow_reference=0.
                By default, the value is 3.
            current_depth: This is used internally to identify current
                recursion depth. Therefore, you should leave this value as-is.
                By default, the value is 0.
            *args, **kwargs: Any arguments, keyword arguments to
                tell json.dumps.
        """
        use_db_field = kwargs.pop('use_db_field', True)
        follow_reference = kwargs.pop("follow_reference", False)
        max_depth = kwargs.pop("max_depth", 3)
        current_depth = kwargs.pop("current_depth", 0)

        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder
        data = self.to_mongo(use_db_field)
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id", None)

        if follow_reference and (
            current_depth < max_depth or max_depth is None
        ):
            data.update(self._follow_reference(
                max_depth, current_depth, use_db_field, *args, **kwargs
            ))
        return json.dumps(data, *args, **kwargs)

    @classmethod
    def from_json(cls, json_str, *args, **kwargs):
        """Decode from human-readable json."""
        hook = generate_object_hook(cls)
        if "object_hook" not in kwargs:
            kwargs["object_hook"] = hook
        dct = json.loads(json_str, *args, **kwargs)
        for fldname, fld in cls.__dict__.items():
            target = fld
            if not isinstance(target, (db.ReferenceField, db.ListField)):
                continue

            islist = isinstance(target, db.ListField)
            value = dct.get(fldname)
            if islist:
                target = target.field
            dct.update({
                fldname: (
                    target.document_type_obj(_created=False, **(value.id))
                ) if isinstance(value, dict) else [
                    target.document_type_obj(
                        _created=False, **(v.id)
                    ) for v in value
                ] if isinstance(value, list) else value
            })
            from pprint import pprint
            pprint(dct)
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
