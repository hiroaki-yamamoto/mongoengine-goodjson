#!/usr/bin/env python
# coding=utf-8

"""Fixtures for integration tests."""

from bson import ObjectId
from six import text_type

from ..schema import Reference, ExtraReference, ExtraInformation
from .articles import article, article_dict
from .user import user_dict

reference_extra_info = ExtraInformation(txt="This is a test")
reference_extra_ref = ExtraReference(pk=ObjectId(), ref_txt="Reference test")
reference_extra_refs = [
    ExtraReference(pk=ObjectId(), ref_txt=("Reference test {}").format(ct))
    for ct in range(3)
]

reference = Reference(
    pk=ObjectId(), name="test", references=[article],
    ex_info=reference_extra_info, ex_ref=reference_extra_ref,
    ex_refs=reference_extra_refs
)
reference_dict = {
    u"id": text_type(reference.id),
    u"name": u"test",
    u"references": [article_dict.copy()],
    u"ex_info": {
        u"txt": reference_extra_info.txt
    },
    u"ex_ref": {
        u"id": str(reference_extra_ref.id),
        u"ref_txt": reference_extra_ref.ref_txt
    },
    u"ex_refs": [
        {u"id": str(item.id), u"ref_txt": item.ref_txt}
        for item in reference_extra_refs
    ]
}
reference_dict["references"][0]["user"] = user_dict.copy()
