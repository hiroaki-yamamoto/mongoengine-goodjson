#!/usr/bin/env python
# coding=utf-8

"""Documents implementing human-readable JSON serializer."""

import json
import types

import mongoengine as db
from bson import SON, DBRef, ObjectId
from .encoder import GoodJSONEncoder
from .decoder import generate_object_hook
from .queryset import QuerySet
from .utils import singledispatch, normalize_reference, id_first


class Helper(object):
    """Helper class to serialize / deserialize JSON document."""

    def __get_doc(self, fld, fldname, value):
        """Get the target document."""
        # Honestly, I don't feel this implementation is good.
        # However, as #892 at MongoEngine
        # (https://github.com/MongoEngine/mongoengine/issues/892)
        # shows, to keep follow reference, this is only the way...
        #
        # (Of course, PR is appreciated.)
        try:
            doc = getattr(self, fldname, None)
        except db.DoesNotExist:
            doc = self._fields[fldname].document_type.objects(id=value).get()
        return fld.document_type.objects(id=doc.id).get() \
            if isinstance(doc, DBRef) else doc

    def __follow_reference_list(self, fld, fldname, *args, **kwargs):
        """Follow reference with list."""
        value = []
        for doc in getattr(self, fldname, []):
            tdoc = fld.document_type.objects(
                id=doc.id
            ).get() if isinstance(doc, DBRef) else doc
            dct = self.__serialize_doc_to_dict(fld, tdoc, *args, **kwargs)
            value.append(id_first(dct))
        return value

    def __follow_reference_dict(self, fld, fldname, *args, **kwargs):
        """Follow reference with dict."""
        value = {}
        for (key, doc) in getattr(self, fldname).items():
            tdoc = fld.document_type.objects(
                id=doc.id
            ).get() if isinstance(doc, DBRef) else doc
            dct = self.__serialize_doc_to_dict(fld, tdoc, *args, **kwargs)
            value[key] = id_first(dct)
        return value

    def __serialize_doc_to_dict(self, fld, doc, *args, **kwargs):
        """Serialize the document into dict."""
        dct = json.loads(doc.to_json(
            *args, **kwargs
        )) if issubclass(
            fld.document_type, Helper
        ) else doc.to_mongo()
        if "_id" in dct:
            dct["id"] = dct.pop("_id")
        return dct

    def _follow_reference(self, max_depth, current_depth,
                          use_db_field, data, *args, **kwargs):
        from .fields import FollowReferenceField
        ret = {}
        for fldname in self:
            fld = self._fields.get(fldname)
            is_list = isinstance(fld, db.ListField)
            is_dict = isinstance(fld, db.DictField)
            target = fld.field if is_list or is_dict else fld

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
                    value = self.__follow_reference_list(
                        target, fldname, *args, **ckwargs
                    )
                elif is_dict:
                    value = self.__follow_reference_dict(
                        target, fldname, *args, **ckwargs
                    )
                else:
                    tdoc = self.__get_doc(target, fldname, data.get(fldname))
                    if tdoc:
                        value = self.__serialize_doc_to_dict(
                            target, tdoc, *args, **ckwargs
                        )
                if value is not None:
                    ret[fldname] = value
                    # ret.update({fldname: value})
        return id_first(ret)

    def __apply_element(
        self, name, fld, cur_depth, func, flagfunc_attr=None
    ):
        """Apply field flag by calling parameter func."""
        from mongoengine_goodjson.fields import FollowReferenceField

        @singledispatch
        def recursive_apply_flag(fld):
            func(fld, cur_depth)

        @recursive_apply_flag.register(db.ListField)
        def set_flag_list(fld):
            if fld.field:
                recursive_apply_flag(fld.field)

        @recursive_apply_flag.register(db.EmbeddedDocumentField)
        def set_flag_emb(fld):
            if issubclass(fld.document_type_obj, Helper):
                obj = getattr(self, name)
                if isinstance(obj, list):
                    for item in obj:
                        getattr(item, flagfunc_attr)()
                elif obj:
                    getattr(obj, flagfunc_attr)(cur_depth)

        @recursive_apply_flag.register(FollowReferenceField)
        def set_flag_self(fld):
            func(fld, cur_depth)

        recursive_apply_flag(fld)

    def __set_gj_flag_sub_field(self, name, fld, cur_depth):
        """Tell current depth to subfield."""
        def set_good_json(traget, depth_lv):
            setattr(traget, "$$cur_depth$$", depth_lv)

        self.__apply_element(
            name, fld, cur_depth, set_good_json, "begin_goodjson"
        )

    def __unset_gj_flag_sub_field(self, name, fld, cur_depth):
        """Remove current depth to subfield."""
        def unset_flag(fld, depth_lv):
            setattr(fld, "$$cur_depth$$", depth_lv - 1)
            cur_depth_attr = getattr(fld, "$$cur_depth$$")
            if (not isinstance(cur_depth_attr, int)) or cur_depth_attr < 0:
                delattr(fld, "$$cur_depth$$")

        self.__apply_element(
            name, fld, cur_depth, unset_flag, "end_goodjson"
        )

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
        current_depth = kwargs.pop("current_depth", 0)
        kwargs.setdefault("cls", GoodJSONEncoder)

        data = self.to_mongo(
            use_db_field, cur_depth=current_depth, good_json=True
        )
        if "_id" in data:
            data.setdefault("id", data.pop("_id", None))

        if follow_reference:
            max_depth_value = None
            try:
                max_depth_value = max_depth(self, current_depth)
            except TypeError:
                max_depth_value = max_depth
            max_depth_value = max_depth_value or 0

            if not (0 < max_depth_value <= current_depth):
                data.update(self._follow_reference(
                    max_depth, current_depth, use_db_field,
                    data, *args, **kwargs
                ))

        data = id_first(self.__to_json_drop_excluded_data(data))
        ret = json.dumps(data, *args, **kwargs)

        return ret

    @classmethod
    def from_json(cls, json_str, created=False, *args, **kwargs):
        # Proposition: add a private method like from_json that allows
        # dictionaries to be used as inputs to avoid having to use
        # loads(dumps(data)) all the time
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

        atLeastOneReference = False

        for fldname, fld in cls._fields.items():
            if isinstance(fld, db.ListField):
                target = fld.field
                if not isinstance(target, db.ReferenceField) or \
                        isinstance(target, FollowReferenceField):
                    continue

                atLeastOneReference = True
                values = dct.get(fldname)
                setattr(
                    from_son_result, fldname, []
                )
                for value in values:
                    valueDoc = value.as_doc()
                    if 'id' not in valueDoc['$id']:
                        valueDoc['$id']['id'] = str(ObjectId())
                    getattr(from_son_result, fldname).append(
                        target.document_type_obj.from_json(
                            json.dumps(value.as_doc()['$id'])
                        )
                    )
            elif isinstance(fld, db.DictField):
                target = fld.field
                if not isinstance(target, db.ReferenceField) or \
                        isinstance(target, FollowReferenceField):
                    continue

                atLeastOneReference = True
                values = dct.get(fldname)
                setattr(
                    from_son_result, fldname, {}
                )
                for k, value in values.items():
                    valueDoc = value.as_doc()
                    if 'id' not in valueDoc['$id']:
                        valueDoc['$id']['id'] = str(ObjectId())
                    getattr(from_son_result, fldname)[k] = \
                        target.document_type_obj.from_json(
                            json.dumps(valueDoc['$id']))
            else:
                target = fld

                if not isinstance(target, db.ReferenceField) or \
                        isinstance(target, FollowReferenceField):
                    continue

                atLeastOneReference = True
                value = dct.get(fldname)

                try:
                    valueDoc = value.as_doc()
                    # If there is no ID in the JSON (aka the JSON was not saved
                    # from mongoengine but rather created manually), create an
                    # ObjectId on the fly
                    if 'id' not in valueDoc['$id']:
                        valueDoc['$id']['id'] = ObjectId()
                    valueDoc['$id']['id'] = str(valueDoc['$id']['id'])
                    setattr(
                        from_son_result,
                        fldname,
                        target.document_type_obj.from_json(
                            json.dumps(valueDoc['$id']))
                    )
                except TypeError:
                    setattr(
                        from_son_result, fldname,
                        normalize_reference(
                            getattr(value, "id", value), target)
                    )

        # All fields have been changed, because the document was loaded from a
        # JSON file. However, mongoengine does not detect it automatically. In
        # order for all fields to be saved, we set the _changed_fields variable
        # manually
        from_son_result._changed_fields = list(cls._fields.keys())

        if atLeastOneReference:
            # If the document contains at least one reference, override the
            # save() method to save the referenced documents at the same time
            # as the master document. Otherwise, the referenced documents would
            # not be saved and the document would not be valid anymore after a
            # save and load from the database.
            def save(self, *args, **kwargs):
                for fldname, fld in cls._fields.items():
                    if isinstance(fld, (db.ReferenceField,
                                        FollowReferenceField)):
                        getattr(self, fldname).save(*args, **kwargs)
                    elif isinstance(fld, db.fields.ComplexBaseField):
                        isReferences = isinstance(
                            fld.field, (db.ReferenceField,
                                        FollowReferenceField))
                        if isinstance(fld, db.DictField) and isReferences:
                            field = getattr(self, fldname)
                            for key, value in field.items():
                                field[key].save(*args, **kwargs)
                        elif isinstance(fld, db.ListField) and isReferences:
                            field = getattr(self, fldname)
                            for valueIndex in range(len(field)):
                                field[valueIndex].save(*args, **kwargs)
                super(self.__class__, self).save(*args, **kwargs)

            from_son_result.save = types.MethodType(save, from_son_result)

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
