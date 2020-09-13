#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Custom Document Base."""

from bson import SON, json_util


class CustomDocumentBase(object):
    """Base document."""

    def to_mongo(self, *args, **kwargs) -> SON:
        """Wrap to_mongo."""
        raw = kwargs.pop("raw", False)
        son = super().to_mongo(*args, **kwargs)
        if all([not raw, "_id" in son, "id" not in son]):
            son["id"] = son.pop("_id")
        return son

    def to_json(self, *args, **kwargs) -> str:
        """
        Convert this document to JSON.

        Parameters:
            use_db_field: Serialize field names as they appear in
                MongoDB (as opposed to attribute names on this document).
                Defaults to True.
            raw: Set True to generate MongoDB Extended JSON.
        """
        use_db_field = kwargs.pop("use_db_field", True)
        raw = kwargs.pop("raw", False)
        if not raw:
            for (fldname, fld) in self._fields.items():
                setattr(fld, "$$mode$$", "json")
        ret = json_util.dumps(
            self.to_mongo(use_db_field, raw=raw), *args, **kwargs,
        )
        if not raw:
            for (fldname, fld) in self._fields.items():
                delattr(fld, "$$mode$$")
        return ret
