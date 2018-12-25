#!/usr/bin/env python
# coding=utf-8

"""Follow Reference Field code."""

import logging

from bson import SON
import mongoengine as db
from ..document import Document
from ..utils import method_dispatch, id_first

log = logging.getLogger(__name__)


class FollowReferenceField(db.ReferenceField):
    """
    Follow Reference Field.

    This field can be treated as a field like ReferenceField, but generates
    the JSON/dict of the referenced document like embedded document.

    Note:
        This field doesn't check recursion level. Therefore, please be careful
        for self-referenced document.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class.

        Parameters:
            *args, **kwsrgs: Any arguments to be passed to ReferenceField.
        Keyword Arguments:
            id_check: Set False to disable id check. By default, this value is
                True
            autosave: Set True to save/update the referenced document when
                to_python is called.
            max_depth: Set natural value to set depath limit for
                loop-reference. By default this value is set to 3.

        """
        self.id_check = kwargs.pop("id_check", True)
        self.autosave = kwargs.pop("autosave", False)
        self.max_depth = kwargs.pop("max_depth", None) or 3
        self.parent_docs = {}
        super(FollowReferenceField, self).__init__(*args, **kwargs)
        if isinstance(self.max_depth, int) and \
                self.max_depth < 0 and self.document_type_obj is \
                db.fields.RECURSIVE_REFERENCE_CONSTANT:
            log.warn(
                "[BE CAREFUL!] Unlimited self reference might cause "
                "infinity loop! [BE CAREFUL!]"
            )

    def __get_doc_parent_pair(self, document, **kwargs):
        """Return document that this field has."""
        doc = document
        if isinstance(doc, db.Document):
            if doc.pk is None and self.id_check:
                self.error("The referenced document needs ID.")
        else:
            try:
                doc = self.document_type.objects(
                    pk=super(
                        FollowReferenceField, self
                    ).to_mongo(document, **kwargs)
                ).get()
            except db.DoesNotExist:
                doc = None
        return doc

    @method_dispatch
    def __get_doc_dict(self, doc, **kwargs):
        kwargs.pop("cur_depth", None)
        kwargs.pop("good_json", None)
        return doc.to_mongo(**kwargs)

    @__get_doc_dict.register(Document)
    def __get_gjdoc_dict(self, doc, **kwargs):
        return doc.to_mongo(**kwargs)

    def to_mongo(self, document, **kwargs):
        """
        Convert to python-typed dict.

        Parameters:
            document: The document.

        """
        doc = self.__get_doc_parent_pair(document, **kwargs)
        cur_depth = getattr(self, "$$cur_depth$$", None)
        max_depth = self.max_depth
        stop = False

        try:
            stop = max_depth(doc, cur_depth)
        except TypeError:
            stop = all([
                max_depth > -1,
                isinstance(cur_depth,  int) and cur_depth >= max_depth
            ])

        stop = (cur_depth is None) or stop

        if stop:
            return super(
                FollowReferenceField, self
            ).to_mongo(document, **kwargs)

        ret = self.__get_doc_dict(
            doc, cur_depth=cur_depth + 1, good_json=True, **kwargs
        )
        if issubclass(self.document_type, Document):
            ret.setdefault("id", ret.pop("_id", None))
        return id_first(ret)

    def to_python(self, value):
        """
        Convert to python-based object.

        Parameters:
            value: The python-typed document.

        """
        clone = value
        if isinstance(value, dict):
            clone = self.document_type._from_son(
                SON(value), created="id" not in value
            )
            if self.autosave:
                clone.save()
        ret = super(FollowReferenceField, self).to_python(clone)
        return ret
