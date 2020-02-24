#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Document."""

from bson import SON

from mongoengine.document import Document as OrigDoc
from .custom import CustomDocumentBase


class Document(CustomDocumentBase, OrigDoc):
    """Base document."""

    meta = {
        "abstract": True,
    }

    def to_mongo(self, *args, **kwargs) -> SON:
        """Wrap to_mongo."""
        son = super().to_mongo(*args, **kwargs)
        from pprint import pprint
        pprint(son)
        if "_id" in son and "id" not in son:
            son["id"] = son.pop("_id")
        return son
