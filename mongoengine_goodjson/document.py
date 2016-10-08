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

    def __set_gj_flag_sub_field(self, instance, fld):
        """Set $$good_json$$ flag to subfield."""
        from mongoengine_goodjson.fields import FollowReferenceField

        @singledispatch
        def set_flag_recursive(fld, instance):
            setattr(fld, "$$good_json$$", True)

        @set_flag_recursive.register(db.ListField)
        def set_flag_list(fld, instance):
            setattr(fld.field, "$$good_json$$", True)

        @set_flag_recursive.register(db.EmbeddedDocumentField)
        def set_flag_emb(fld, instance):
            if isinstance(instance, Helper):
                instance.begin_goodjson()

        @set_flag_recursive.register(FollowReferenceField)
        def set_flag_self(fld, instance):
            setattr(fld, "$$good_json$$", True)
            setattr(fld.document_type, "$$good_json$$", True)

        set_flag_recursive(fld, instance)

    def __unset_gj_flag_sub_field(self, instance, fld):
        """Unset $$good_json$$ to subfield."""
        from mongoengine_goodjson.fields import FollowReferenceField

        def unset_flag(fld):
            setattr(fld, "$$good_json$$", None)
            delattr(fld, "$$good_json$$")

        @singledispatch
        def unset_flag_recursive(fld, instance):
            unset_flag(fld)

        @unset_flag_recursive.register(db.ListField)
        def unset_flag_list(fld, instance):
            unset_flag(fld.field)

        @unset_flag_recursive.register(db.EmbeddedDocumentField)
        def unset_flag_emb(fld, instance):
            if isinstance(instance, Helper):
                instance.end_goodjson()

        @unset_flag_recursive.register(FollowReferenceField)
        def unset_flag_self(fld, instance):
            unset_flag(fld)
            unset_flag(fld.document_type)

        unset_flag_recursive(fld, instance)

    def begin_goodjson(self):
        """Enable GoodJSON Flag."""
        for (name, fld) in self._fields.items():
            self.__set_gj_flag_sub_field(getattr(self, name), fld)

    def end_goodjson(self):
        """Stop GoodJSON Flag."""
        for (name, fld) in self._fields.items():
            self.__unset_gj_flag_sub_field(getattr(self, name), fld)

    def to_mongo(self, *args, **kwargs):
        """Convert into mongodb compatible dict."""
        if getattr(self, "$$good_json$$", None):
            self.begin_goodjson()
        result = super(Helper, self).to_mongo(*args, **kwargs)
        if getattr(self, "$$good_json$$", None):
            self.end_goodjson()
        return result

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

        self.begin_goodjson()

        data = self.to_mongo(use_db_field)
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id", None)

        for name, fld in self._fields.items():
            if any([
                getattr(fld, "exclude_to_json", None),
                getattr(fld, "exclude_json", None)
            ]):
                data.pop(name, None)

        if follow_reference and \
                (current_depth < max_depth or max_depth is None):
            data.update(self._follow_reference(
                max_depth, current_depth, use_db_field, *args, **kwargs
            ))

        self.end_goodjson()

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
        for name, fld in cls._fields.items():
            if any([
                getattr(fld, "exclude_from_json", None),
                getattr(fld, "exclude_json", None)
            ]):
                dct.pop(name, None)
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

        for fldname, fld in cls._fields.items():
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
