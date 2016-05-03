#!/usr/bin/env python
# coding=utf-8

"""Documents implementing human-readable JSON serializer."""

import json

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

import mongoengine as db
from bson import SON, DBRef
from .encoder import GoodJSONEncoder
from .decoder import generate_object_hook
from .queryset import QuerySet


class Helper(object):
    """Helper class to serialize / deserialize JSON document."""

    def _follow_reference(self, max_depth, current_depth,
                          use_db_field, *args, **kwargs):
        from .fields import FollowReferenceField
        ret = {}
        for fldname in self:
            fld = self._fields.get(fldname)
            is_list = isinstance(fld, db.ListField)
            target = fld.field if is_list else fld

            if all([
                isinstance(
                    target, (db.ReferenceField, db.EmbeddedDocumentField)
                ), not isinstance(target, FollowReferenceField)
            ]):
                value = None
                if is_list:
                    value = []
                    for doc in getattr(self, fldname, []):
                        value.append(json.loads((
                            target.document_type.objects(
                                id=doc.id
                            ).get() if isinstance(doc, DBRef) else doc
                        ).to_json(
                            follow_reference=True,
                            max_depth=max_depth,
                            current_depth=current_depth + 1,
                            use_db_field=use_db_field,
                            *args, **kwargs
                        )))
                else:
                    doc = getattr(self, fldname, None)
                    value = json.loads(
                        (
                            target.document_type.objects(
                                id=doc.id
                            ).get() if isinstance(doc, DBRef) else doc
                        ).to_json(
                            follow_reference=True,
                            max_depth=max_depth,
                            current_depth=current_depth + 1,
                            use_db_field=use_db_field,
                            *args, **kwargs
                        )
                    ) if doc else doc
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

        if follow_reference and \
                (current_depth < max_depth or max_depth is None):
            data.update(self._follow_reference(
                max_depth, current_depth, use_db_field, *args, **kwargs
            ))

        return json.dumps(data, *args, **kwargs)

    @classmethod
    def from_json(cls, json_str, created=False, *args, **kwargs):
        """
        Decode from human-readable json.

        Parameters:
            json_str: JSON string that should be passed to the serialized
            created: a parameter that is passed to cls._from_son.
            *args, **kwargs: Any additional arguments that is passed to
                json.loads.
        """
        from .fields import FollowReferenceField
        hook = generate_object_hook(cls)
        if "object_hook" not in kwargs:
            kwargs["object_hook"] = hook
        dct = json.loads(json_str, *args, **kwargs)
        from_son_result = cls._from_son(SON(dct), created=created)

        @singledispatch
        def normalize_reference(ref_id, fld):
            """Normalize Reference."""
            return ref_id and fld.to_python(ref_id) or None

        @normalize_reference.register(dict)
        def normalize_reference_dict(ref_id, fld):
            """Normalize Reference for dict."""
            return fld.to_python(ref_id["id"])

        @normalize_reference.register(list)
        def normalize_reference_list(ref_id, fld):
            """Normalize Reference for list."""
            return [
                normalize_reference(ref.id, fld) for ref in ref_id
            ]

        for fldname, fld in cls.__dict__.items():
            target = fld.field if isinstance(fld, db.ListField) else fld

            if not isinstance(target, db.ReferenceField) or \
                    isinstance(target, FollowReferenceField):
                continue

            value = dct.get(fldname)
            setattr(
                from_son_result, fldname,
                normalize_reference(getattr(value, "id", value), target)
            )
        return from_son_result


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
