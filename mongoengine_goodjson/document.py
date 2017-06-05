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
                          use_db_field, data, *args, **kwargs):
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
                ckwargs = kwargs.copy()
                if issubclass(target.document_type, Helper):
                    ckwargs.update({
                        "follow_reference": True,
                        "max_depth": max_depth,
                        "current_depth": current_depth + 1,
                        "use_db_field": use_db_field
                    })
                if is_list:
                    value = []
                    for doc in getattr(self, fldname, []):
                        tdoc = target.document_type.objects(
                            id=doc.id
                        ).get() if isinstance(doc, DBRef) else doc
                        dct = json.loads(tdoc.to_json(
                            *args, **ckwargs
                        )) if issubclass(
                            target.document_type, Helper
                        ) else tdoc.to_mongo()
                        if "_id" in dct:
                            dct["id"] = dct.pop("_id")
                        value.append(dct)
                else:
                    # Honestly, I don't feel this implementation is good.
                    # However, as #892 at MongoEngine
                    # (https://github.com/MongoEngine/mongoengine/issues/892)
                    # shows, to keep follow reference, this is only the way...
                    #
                    # (Of course, PR is appreciated.)
                    try:
                        doc = getattr(self, fldname, None)
                    except db.DoesNotExist:
                        doc = self._fields[fldname].document_type.objects(
                            id=data[fldname]
                        ).get()
                    tdoc = target.document_type.objects(
                        id=doc.id
                    ).get() if isinstance(doc, DBRef) else doc
                    value = json.loads(
                        tdoc.to_json(*args, **ckwargs)
                    ) if issubclass(
                        target.document_type, Helper
                    ) else tdoc.to_mongo() if doc else doc
                    if "_id" in value:
                        value["id"] = value.pop("_id")
                if value is not None:
                    ret[fldname] = value
                    # ret.update({fldname: value})
        return ret

    def __set_gj_flag_sub_field(self, name, fld, cur_depth):
        """Tell current depth to subfield."""
        from mongoengine_goodjson.fields import FollowReferenceField

        def set_good_json(traget):
            setattr(traget, "$$cur_depth$$", cur_depth)

        @singledispatch
        def set_flag_recursive(fld):
            set_good_json(fld)

        @set_flag_recursive.register(db.ListField)
        def set_flag_list(fld):
            set_flag_recursive(fld.field)

        @set_flag_recursive.register(db.EmbeddedDocumentField)
        def set_flag_emb(fld):
            if issubclass(fld.document_type_obj, Helper):
                obj = getattr(self, name)
                if isinstance(obj, list):
                    for item in obj:
                        item.begin_goodjson()
                else:
                    obj.begin_goodjson(cur_depth)

        @set_flag_recursive.register(FollowReferenceField)
        def set_flag_self(fld):
            set_good_json(fld)

        set_flag_recursive(fld)

    def __unset_gj_flag_sub_field(self, name, fld, cur_depth):
        """Remove current depth to subfield."""
        from mongoengine_goodjson.fields import FollowReferenceField

        def unset_flag(fld):
            setattr(fld, "$$cur_depth$$", cur_depth - 1)
            cur_depth_attr = getattr(fld, "$$cur_depth$$")
            if (not isinstance(cur_depth_attr, int)) or cur_depth_attr < 0:
                delattr(fld, "$$cur_depth$$")

        @singledispatch
        def unset_flag_recursive(fld):
            unset_flag(fld)

        @unset_flag_recursive.register(db.ListField)
        def unset_flag_list(fld):
            unset_flag_recursive(fld.field)

        @unset_flag_recursive.register(db.EmbeddedDocumentField)
        def unset_flag_emb(fld):
            if issubclass(fld.document_type_obj, Helper):
                obj = getattr(self, name)
                if isinstance(obj, list):
                    for item in obj:
                        item.end_goodjson()
                else:
                    obj.end_goodjson(cur_depth)

        @unset_flag_recursive.register(FollowReferenceField)
        def unset_flag_self(fld):
            unset_flag(fld)

        unset_flag_recursive(fld)

    def begin_goodjson(self, cur_depth=0):
        """Enable GoodJSON Flag."""
        for (name, fld) in self._fields.items():
            self.__set_gj_flag_sub_field(name, fld, cur_depth=cur_depth)

    def end_goodjson(self, cur_depth=0):
        """Stop GoodJSON Flag."""
        for (name, fld) in self._fields.items():
            self.__unset_gj_flag_sub_field(name, fld, cur_depth=cur_depth)

    def to_mongo(self, *args, **kwargs):
        """Convert into mongodb compatible dict."""
        cur_depth = kwargs.pop("cur_depth", None) or 0
        good_json = bool(kwargs.pop("good_json", False))
        if good_json:
            self.begin_goodjson(cur_depth)
        result = super(Helper, self).to_mongo(*args, **kwargs)
        if good_json:
            self.end_goodjson(cur_depth)
        return result

    def __to_json_drop_excluded_data(self, data, flds=None):
        """
        Cosider exclude_to_json and exclude_json flag.

        Arguments:
            data: The return value of to_mongo from the top-level document.
            flds: The fields of child document. In usual use, this parameter
                should be None, because this is used internally.
        """
        ret = data.copy()
        for name, fld in (flds or self._fields).items():
            if any([
                getattr(fld, "exclude_to_json", None),
                getattr(fld, "exclude_json", None)
            ]):
                ret.pop(name, None)
            elif isinstance(ret.get(name), list):
                if isinstance(fld.field, db.EmbeddedDocumentField) and \
                        issubclass(fld.field.document_type, Helper):
                    ret[name] = [
                        self.__to_json_drop_excluded_data(
                            item, fld.field.document_type._fields
                        ) for item in ret[name]
                    ]
            elif isinstance(ret.get(name), dict) and \
                    hasattr(fld, "document_type"):
                ret[name] = self.__to_json_drop_excluded_data(
                    ret[name], fld.document_type._fields
                )
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
            *args, **kwargs: Any arguments, and keyword arguments to
                tell json.dumps.

        """
        use_db_field = kwargs.pop('use_db_field', True)
        follow_reference = kwargs.pop("follow_reference", False)
        max_depth = kwargs.pop("max_depth", 3)
        current_depth = kwargs.pop("current_depth", 0) or 0

        if "cls" not in kwargs:
            kwargs["cls"] = GoodJSONEncoder

        data = self.to_mongo(
            use_db_field, cur_depth=current_depth, good_json=True
        )
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id", None)

        if follow_reference:
            max_depth_value = None
            func_call = False
            try:
                max_depth_value = max_depth(self, current_depth)
                func_call = True
            except TypeError:
                max_depth_value = max_depth

            if (func_call and not max_depth_value) or (
                isinstance(max_depth_value, int) and (
                    current_depth < max_depth_value or max_depth_value < 0
                )
            ) or max_depth_value is None:
                data.update(
                    self._follow_reference(
                        max_depth, current_depth, use_db_field,
                        data, *args, **kwargs
                    )
                )

        data = self.__to_json_drop_excluded_data(data)

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
        kwargs.setdefault("object_hook", generate_object_hook(cls))
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
            return fld.to_python(ref_id.get("id") or ref_id["_id"])

        @normalize_reference.register(list)
        def normalize_reference_list(ref_id, fld):
            """Normalize Reference for list."""
            return [normalize_reference(ref.id, fld) for ref in ref_id]

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
