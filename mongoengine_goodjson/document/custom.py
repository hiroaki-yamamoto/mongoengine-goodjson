#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Custom Document Base."""

from bson import SON, json_util


class CustomDocumentBase(object):
    """Base document."""

    def to_mongo(self, use_db_field=True, fields=None, to_json=False):
        """Return as SON data ready for use with MongoDB."""
        # Note: this function is copied from official repo, except
        # JSON serialization related stuff
        fields = fields or []

        data = SON()
        data["_id"] = None
        data["_cls"] = self._class_name

        # only root fields ['test1.a', 'test2'] => ['test1', 'test2']
        root_fields = {f.split(".")[0] for f in fields}

        for field_name in self:
            if root_fields and field_name not in root_fields:
                continue

            value = self._data.get(field_name, None)
            field = self._fields.get(field_name)

            if field is None and self._dynamic:
                field = self._dynamic_fields.get(field_name)

            if value is not None:
                f_inputs = field.to_mongo.__code__.co_varnames
                ex_vars = {}
                if fields and "fields" in f_inputs:
                    key = "%s." % field_name
                    embedded_fields = [
                        i.replace(key, "") for i in fields if i.startswith(key)
                    ]

                    ex_vars["fields"] = embedded_fields

                if "use_db_field" in f_inputs:
                    ex_vars["use_db_field"] = use_db_field
                # ## This is the custom part: add to_json flag
                # ## to check whether caller is to_json or not.
                try:
                    value = field.to_mongo(value, to_json=to_json, **ex_vars)
                except (NameError, TypeError):
                    value = field.to_mongo(value, **ex_vars)
                # ## End of the custom part

            # Handle self generating fields
            if value is None and field._auto_gen:
                value = field.generate()
                self._data[field_name] = value

            if (value is not None) or (field.null):
                if use_db_field:
                    data[field.db_field] = value
                else:
                    data[field.name] = value
        if not data.get("_id"):
            data.pop("_id", None)
        # Only add _cls if allow_inheritance is True
        if not self._meta.get("allow_inheritance"):
            data.pop("_cls")

        return data

    def to_json(self, *args, **kwargs):
        """
        Convert this document to JSON.

        Parameters:
            use_db_field: Serialize field names as they appear in
                MongoDB (as opposed to attribute names on this document).
                Defaults to True.
        """
        use_db_field = kwargs.pop("use_db_field", True)
        return json_util.dumps(
            self.to_mongo(use_db_field, to_json=True), *args, **kwargs,
        )
